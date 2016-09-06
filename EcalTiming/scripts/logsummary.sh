DO=$1
echo \#Run RecoPassed
grep  "TrigReport Events"  log/stderr-AlCaPhiSym-*_RECO.log | awk '{ counts[substr($1,23,6)]+=$8} END{for (i in counts) printf "%s\t%7.2fM\n", i,counts[i]/1000000}' |sort 
echo \#Run AnalysisPassed
grep  "TrigReport Events"  log/stderr-AlCaPhiSym-*-1.log | awk '{ counts[substr($1,23,6)]+=$8} END{for (i in counts) printf "%s\t%7.2fM\n", i,counts[i]/1000000}' |sort 
echo \#Failed Jobs
failed=$(grep -L "TrigReport Events" log/stderr-AlCaPhiSym-*)
for stderr in $failed;
do
	job=${stderr:11}
	job=${job%%--*}
	echo $job
	if [[ $DO == *"RESUB"* ]]
	then
		runcommand=$(sed -n '15,15p;16q' ${stderr/err/out})
		bsub -oo ${stderr/err/out} -eo $stderr -R "rusage[mem=4000]" -q cmscaf1nd "cd $PWD; eval \`scramv1 runtime -sh\`; cd -
		${runcommand}
		" || exit 1
	fi
done
