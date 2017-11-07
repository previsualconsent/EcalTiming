#!/bin/bash
if ! klist -s
	then kinit
fi

env -i $(env |grep KRB) cern-get-sso-cookie --krb -r -u https://cmswbm.web.cern.ch/ -o ~/private/ssocookie.txt
exit

RUN_BEGIN=294847
RUN_END=305517
URL="https://cmswbm.web.cern.ch/cmswbm/cmsdb/servlet/RunSummary?DB=default&SUBMIT_TOP=SubmitQuery&RUN_BEGIN=${RUN_BEGIN}&RUN_END=${RUN_END}&STATUS_ECAL=on" 
RUNSUMMARYFILE=runsummary_${RUN_BEGIN}_${RUN_END}.html
wget --load-cookies ~/private/ssocookie.txt -O ${RUNSUMMARYFILE} $URL

sed -i -n '/TABLE/,$p' ${RUNSUMMARYFILE}

./scripts/getRunTable.py $RUNSUMMARYFILE |sort -n > data/${RUNSUMMARYFILE%.*}.dat

rm ${RUNSUMMARYFILE}
