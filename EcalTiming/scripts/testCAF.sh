#RUNLIST="251244 251251 251252 251521 251522 251548 251559 251560 251561 251562"
#2015B
#RUNLIST="251643 251721 251883"
#RUNPERIOD=Run2015B-v1
#2015C
#RUNLIST="254231 254232 254790 254879" #254852 
RUNPERIOD=2016A-v1

#RUNLIST="254292 254293 254294 254319 254332 254341 254342 254349 254458 254459 254608"
#RUNLIST="254307 255981 256001 256002 256003 256167 256169 256171 256215 256237" #256245 256349 256350 256355 256406"

#2016A runlist
RUNLIST="270639 270862 270886 270887 271045 271047 271048 271049 271082 271084 271087 271142 271143 271144 271161 271167 271168 271169 271170 271188 271191 271192 271193 271195 271336 271337 271338 271342"
RUNLIST="271195"

STREAM=AlCaPhiSym
NEVENTS=-1
QUEUE=2nd
EOSPREFIX=root://eoscms//eos/cms/
EOSDIR=/store/group/dpg_ecal/alca_ecalcalib/EcalTiming/
#DIR=/afs/cern.ch/work/p/phansen/public/EcalTiming/RunII/
CONFIG=$PWD/test/ecalTime_fromAlcaStream_cfg.py
EVENTSPERJOB=500000
USER=$(whoami)

eos=/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select
STEP=RECOTIMEANALYSIS
for i in "$@"
do
case $i in
    -s=*|--stream=*)
    STREAM="${i#*=}"
    shift # past argument=value
    ;;
    -c=*|--cfg=*)
    CONFIG=$PWD/"${i#*=}"
    shift # past argument=value
    ;;
    -d=*|--dir=*)
    DIR="${i#*=}"
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
    --step=*)
    STEP="${i#*=}"
    shift # past argument=value
    ;;
    --json=*)
    JSON="${i#*=}"
    shift # past argument=value
    ;;
    --runperiod=*)
    RUNPERIOD="${i#*=}"
    shift # past argument=value
    ;;
    --tag=*)
    GLOBALTAG="${i#*=}"
    shift # past argument=value
    ;;
    --eventsperjob=*)
    EVENTSPERJOB="${i#*=}"
    shift # past argument=value
    ;;
    *)
            # unknown option
		echo option $i not defined
		exit 1 
    ;;
esac
done

if [[ -z $GLOBALTAG ]]
then
	echo Tag not set
	exit 1
fi

for RUN in ${RUNLIST}
do
	echo "=== RUN = ${RUN}"
	if [ $JSON ] && ! grep $RUN $JSON > /dev/null;
	then
		echo $RUN not in JSON $JSON
		continue
	fi
	OUTDIR=$EOSDIR/${RUNPERIOD}/${STREAM}-${RUN}/
	$eos mkdir ${EOSDIR}
	$eos mkdir ${OUTDIR}
	AFSDIR=/afs/cern.ch/work/p/phansen/public/EcalTiming/analysis/${RUNPERIOD}/${STREAM}-${RUN}/
	mkdir -p ${AFSDIR}

	if [[ $STEP == *"RECO"* ]]
	then
                echo "doing reco"
		RECO="_RECO"
		nfiles=`das_client.py --query="file dataset=/${STREAM}/${RUNPERIOD}/RAW run=${RUN} | count(file.name)" | sed '2 d'`
		nfiles=${nfiles:19}

		if ! [[ $nfiles =~ ^[0-9]+$ ]]; then
			echo "No Files found"
			continue
		fi

		echo Will run over $nfiles files
		filelist=`das_client.py --query="file dataset=/${STREAM}/${RUNPERIOD}/RAW run=${RUN}" --limit=${nfiles} | sed '2 d'`
		# for file in ${filelist}
		# do
		# das_client.py --query="file=${file} | sum(file.nevents)"
		# done
	else
                echo Not reco
		#filelist=`grep ${RUN}  ~shervin/public/4peter/fileMap-sorted.dat  | cut -d ' ' -f2`
		#filelist=(${OUTDIR}/ecalTiming_*_numEvent50000_RECO.root)
		#filelist=${filelist[@]/#/file://}
		filelist=${OUTDIR}

	fi
	if [[ $STEP == *"TIME"* ]]
	then
		RECO=""
	fi

	if [ "$SPLIT" != "YES" ]
	then
		echo Submitting one job per run
		filelist=`echo ${filelist}| sed 's| |,|g;s|,$||'`
	fi
	
	#jsonFile=/afs/cern.ch/cms/CAF/CMSALCA/ALCA_ECALCALIB/json_ecalonly/251022-251562-Prompt-pfgEcal-noLaserProblem.json

	i=0
	for file in $filelist
	do
		name=${i}
		#let skip=$EVENTSPERJOB*$job
		skip=0
		tmp_file=ecalTiming_${name}.root
		if [ "$NEVENTS" == "-1" ]
		then
			tmp_file_real=ecalTiming_${name}${RECO}.root
		else
			tmp_file_real=ecalTiming_${name}_numEvent${NEVENTS}${RECO}.root
		fi
		runcommand="cmsRun ${CONFIG} files=${file} output=${tmp_file} maxEvents=${NEVENTS} jsonFile=${JSON} minEnergyEB=1.5 minEnergyEE=2.5 step=${STEP} skipEvents=${skip} globaltag=${GLOBALTAG};"
		#runcommand+="ls -l;"
		#runcommand+="df -h;"
		runcommand+="xrdcp ${tmp_file_real} ${EOSPREFIX}${OUTDIR}/;"
		echo "check if file exists"
		if $eos ls ${OUTDIR}/${tmp_file_real}
		then
			echo File exists: ${OUTDIR}/${tmp_file_real}
			let i=i+1
			continue
		fi
		if [[ $STEP == *"TIME"* ]]
		then
			runcommand+="cp ecalTiming_* ${AFSDIR}/;"
		fi
		echo "$runcommand"
		if [ "$BATCH" == "YES" ]
		then
			bsub -oo log/stdout-${STREAM}-${RUN}-${name}-${NEVENTS}${RECO}.log -eo log/stderr-${STREAM}-${RUN}-${name}-${NEVENTS}${RECO}.log -R "rusage[mem=4000]" -q ${QUEUE} "cd $PWD; eval \`scramv1 runtime -sh\`; cd -
			${runcommand}
			" || exit 1
		else
			eval $runcommand
		fi
		let i=i+1
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
