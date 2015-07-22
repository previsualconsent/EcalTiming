RUNLIST="243479 243484 243506"
RUNLIST="248030"
RUNLIST=`cat runlist`
RUNLIST="251244 251251 251252 251521 251522 251548 251559 251560 251561 251562"

STREAM=AlCaPhiSym
NEVENTS=-1
QUEUE=2nd
DIR=/afs/cern.ch/work/p/phansen/public/EcalTiming/round1
CONFIG=test/ecalTime_fromAlcaStream_cfg.py

FROMRECO=NO
for i in "$@"
do
case $i in
    -s=*|--stream=*)
    STREAM="${i#*=}"
    shift # past argument=value
    ;;
    -r=*|--runlist=*)
    RUNLIST="${i#*=}"
	 RUNLIST=${RUNLIST//,/ }
    shift # past argument=value
    ;;
    -n=*|--nevents=*)
    NEVENTS="${i#*=}"
    shift # past argument=value
    ;;
    -q=*|--queue=*)
    QUEUE="${i#*=}"
    shift # past argument=value
    ;;
    -b|--batch)
    BATCH=YES
    shift # past argument with no value
    ;;
    --split)
    SPLIT=YES
    shift # past argument with no value
    ;;
    --fromreco)
    FROMRECO=YES
    shift # past argument with no value
    ;;
    *)
            # unknown option
		echo option $i not defined
    ;;
esac
done

for RUN in ${RUNLIST}
do

	echo "=== RUN = ${RUN}"
	OUTDIR=$DIR/${STREAM}-${RUN}/
	mkdir -p ${OUTDIR}

	if [ "$FROMRECO" == "NO" ]
	then
		filelist=`das_client.py --query="file dataset=/MinimumBias/Commissioning2015-v1/RAW run=${RUN}" --limit=50 | sed '2 d'`
		nfiles=`das_client.py --query="file dataset=/${STREAM}/Run2015B-v1/RAW run=${RUN} | count(file.name)" | sed '2 d'`
		nfiles=${nfiles:19}

		if ! [[ $nfiles =~ ^[0-9]+$ ]]; then
			echo "No Files found"
		exit 1
		fi

		#echo Will run over $nfiles files
		filelist=`das_client.py --query="file dataset=/${STREAM}/Run2015B-v1/RAW run=${RUN}" --limit=${nfiles} | sed '2 d'`
		# for file in ${filelist}
		# do
		# das_client.py --query="file=${file} | sum(file.nevents)"
		# done
	else
		filelist=`grep ${RUN}  ~shervin/public/4peter/fileMap-sorted.dat  | cut -d ' ' -f2`
	fi

	if [ "$SPLIT" != "YES" ]
	then
		echo Submitting one job per run
		filelist=`echo ${filelist}| sed 's| |,|g;s|,$||'`
	fi
	
	jsonFile=/afs/cern.ch/cms/CAF/CMSALCA/ALCA_ECALCALIB/json_ecalonly/251022-251562-Prompt-pfgEcal-noLaserProblem.json

	for en in $(seq 0 .5 4.5)
	do
		i=0
		for file in $filelist
		do
			name=${i}_${en}GeV
			runcommand="cmsRun ${CONFIG} files=${filelist} output=${OUTDIR}/ecalTiming_${name}.root maxEvents=${NEVENTS} jsonFile=${jsonFile} minEnergy=${en}"
			if [ "$BATCH" == "YES" ]
			then
				bsub -oo ${OUTDIR}/stdout_${name}_${NEVENTS}.log -eo ${OUTDIR}/stderr_${name}_${NEVENTS}.log -R "rusage[mem=4000]" -q ${QUEUE} "cd $PWD; eval \`scramv1 runtime -sh\`; 
				${runcommand}
				" || exit 1
			else
				runcommand
			fi
			let i=i+1
		done
	done

done
exit 0
cat > test/run-${RUN}.cfg <<EOF
[CRAB]
jobtype=cmssw
scheduler=CAF


[CMSSW]
datasetpath=/MinimumBias/Commissioning2015-v1/RAW
runselection=${RUN}
pset=python/ecalTimeTreeMaker_FromRaw_CosmicOrBeamSplash_cfg.py
get_edm_output=1
#split_by_run=1
lumis_per_job=10000
total_number_of_lumis=-1
#number_of_jobs=1

[USER]
ui_working_dir=/afs/cern.ch/user/s/shervin/scratch1/CMSSW_7_3_4/src/EcalTiming/EcalTiming/test/run-${RUN}
return_data=1
#outputdir=/afs/cern.ch/user/s/shervin/scratch1/CMSSW_7_3_4/src/EcalTiming/EcalTiming/test/run-${RUN}/output
check_user_remote_dir=1

[CAF]
queue=cmscaf1nd



[GRID]



EOF

done
