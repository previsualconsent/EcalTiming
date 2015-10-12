from collections import namedtuple
from FWCore.PythonUtilities.LumiList import LumiList

jsonFolder="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/"

RunPeriod = namedtuple('RunPeriod',("name","bfield","firstRun","lastRun","json","bunchSpacing","GT"))
runPeriods = []

Run2015AB_json           = jsonFolder + "Cert_246908-255031_13TeV_PromptReco_Collisions15_50ns_JSON_v2.txt"
Run2015AB_ZeroTesla_json = jsonFolder + "Cert_246908-252126_13TeV_PromptReco_Collisions15_ZeroTesla_50ns_JSON.txt"
Run2015CD_json           = jsonFolder + "Cert_246908-256869_13TeV_PromptReco_Collisions15_25ns_JSON.txt"
Run2015CD_ZeroTesla_json = jsonFolder + "Cert_246908-256869_13TeV_PromptReco_Collisions15_ZeroTesla_25ns_JSON.txt"
Run254833_json           = jsonFolder + "Cert_254833_13TeV_PromptReco_Collisions15_JSON.txt"

#Run2015AB           = LumiList(filename = Run2015AB_json          )
#Run2015AB_ZeroTesla = LumiList(filename = Run2015AB_ZeroTesla_json)
#Run2015CD           = LumiList(filename = Run2015CD_json          )
#Run2015CD_ZeroTesla = LumiList(filename = Run2015CD_ZeroTesla_json)
#Run254833           = LumiList(filename = Run254833_json          )

runPeriods.append(RunPeriod("Run2015A-v1", False, 247607, 250932,  Run2015AB_ZeroTesla_json,   50, "GR_P_V56"))
runPeriods.append(RunPeriod("Run2015A-v1", True,  247607, 250932,  Run2015AB_json,             50, "GR_P_V56"))
runPeriods.append(RunPeriod("Run2015B-v1", False, 250985, 253620,  Run2015AB_ZeroTesla_json,   50, "74X_dataRun2_Prompt_v0"))
runPeriods.append(RunPeriod("Run2015B-v1", True,  250985, 253620,  Run2015AB_json,             50, "74X_dataRun2_Prompt_v0"))
runPeriods.append(RunPeriod("Run2015C-v1", False, 253659, 256464,  Run2015CD_ZeroTesla_json,   25, "74X_dataRun2_Prompt_v1"))
runPeriods.append(RunPeriod("Run2015C-v1", True,  253659, 256464,  Run2015CD_json,             25, "74X_dataRun2_Prompt_v1"))
runPeriods.append(RunPeriod("Run2015D-v1", False, 256630, 999999,  Run2015CD_ZeroTesla_json,   25, "74X_dataRun2_Prompt_v2"))
runPeriods.append(RunPeriod("Run2015D-v1", True,  256630, 999999,  Run2015CD_json,             25, "74X_dataRun2_Prompt_v2"))
                                                                
runPeriods.append(RunPeriod("Run2015C-v1", True,  254833, 254833,  Run254833_json,             50, "74X_dataRun2_Prompt_v1"))

def LumiListForRunPeriod(rp):
	ll = LumiList(filename = rp.json)
	runs = [ run for run in map(int,ll.getRuns()) if run >= rp.firstRun and run <= rp.lastRun]
	ll.selectRuns(runs)
	return ll

def getRuns(name=None,bfield=None,bunchSpacing=None):
	ll = LumiList()
	for rp in runPeriods:
		if name is None or rp.name == name:
			if bfield is None or rp.bfield == bfield:
				if bunchSpacing is None or rp.bunchSpacing == bunchSpacing:
					newll = LumiListForRunPeriod(rp)
					ll += LumiListForRunPeriod(rp)
	return ll.getRuns()

def getRunPeriod(name,bfield,bunchSpacing):
	for rp in runPeriods:
		if rp.name == name:
			if rp.bfield == bfield:
				if rp.bunchSpacing == bunchSpacing:
					return rp

import sys

if __name__ == "__main__":
	name = sys.argv[1]
	bfield = bool(int(sys.argv[2]))
	bunchSpacing = int(sys.argv[3])
	rp = getRunPeriod(name,bfield,bunchSpacing)
	ll = LumiListForRunPeriod(rp)
	if not ll.getRuns():
		sys.exit(0)
	options = ""
	options += " -r=" +",".join(map(str,ll.getRuns()))
	options += " --json=" + rp.json
	options += " --tag=" + rp.GT
	options += " --runperiod=" + rp.name
	print options
