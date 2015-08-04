import ROOT
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle, customPalette
import EcalTiming.EcalTiming.loadOldCalib as cal
import os



def fixCCU(input):

	#input = "/afs/cern.ch/user/p/phansen/public/ecal-timing/dump_EcalTimeCalibConstants_v07_offline__since_00204623_till_4294967295.dat"
	customROOTstyle()

	rawidMap = cal.getRawIDMap()

	print_once = set()
	ccu_adj = {(54, 19): 4.0, (54, 20): 4.0, (48,  1): 2.0, (48,  2): 2.0, (48,  7): 2.0, (48,  5): 2.0, (48,  6): 2.0, (48,  3): 2.0, (48,  8): 2.0, (48,  4): 2.0, (1, 31): 4.0}
	output = input.replace("ecalTiming","ecalTiming-fixCCU-v2")
	with open(input,'r') as f:
		with open(output,'w') as of:
			for line in f:
				if "#" in line: continue
				line = line.split()
				start = line[:3]
				end = line[4:]
				time = float(line[3])
				rawid = int(line[-1])

				key = (rawidMap[rawid].FED, rawidMap[rawid].CCU)
				if key in ccu_adj:
					adj = ccu_adj[key] * 25./24.
					if key not in print_once:
						print_once.add(key)
						print key, line, adj
				else:
					adj = 0
				out = "\t".join(start + ["%.4f" %(time - adj)] + end) + '\n'
				of.write(out)

if __name__ == "__main__":
	filename = "/afs/cern.ch/work/p/phansen/public/EcalTiming/Cuts_EB1.0_EE2.0/AlCaPhiSym-251562/ecalTiming_0_GeV_numEvent10000000-corr.dat"
	calib = fixCCU(filename);

