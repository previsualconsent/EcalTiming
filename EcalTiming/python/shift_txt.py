import ROOT
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle, customPalette
import os


def addFitToPlot(h):
	c = ROOT.TCanvas("c","c",800,500)
	c.SetLogy()
	fit = ROOT.TF1("gaus","gaus")
	h.Fit(fit, "Q")
	mu = fit.GetParameter(1)
	sigma = fit.GetParameter(2)
	label = ROOT.TPaveText(.7, .7, .9, .9, "NDC")
	label.AddText("#mu = %.3f" % mu)
	label.AddText("#sigma = %.3f" % sigma)
	label.Draw()
	c.SaveAs(h.GetName() + ".png")
	return mu,sigma

def shiftCalib(input):

	#input = "/afs/cern.ch/user/p/phansen/public/ecal-timing/dump_EcalTimeCalibConstants_v07_offline__since_00204623_till_4294967295.dat"
	customROOTstyle()

	hists = dict()
	for iz in [0,-1,1]:
		hists[iz] =  ROOT.TH1F("time_{iz}".format(iz=iz),"time",100,-10,10)

	with open(input,'r') as f:
		for line in f:
			line = line.split()
			time = float(line[3])
			iz = int(line[2])
			hists[iz].Fill(time)
	
	offset = dict()
	for iz in hists:
		offset[iz],__ = addFitToPlot(hists[iz])

	print offset

	#output = os.path.splitext(input)[0] + "-GlobalOffset.txt"
	output = input.replace("ecalTiming","ecalTimeRelative")
	global_out = input.replace("ecalTiming","ecalTimeGlobal")
	with open(input,'r') as f:
		with open(output,'w') as of:
			for line in f:
				line = line.split()
				start = line[:3]
				end = line[4:]
				time = float(line[3])
				iz = int(line[2])

				out = "\t".join(start + ["%.3f" %(time - offset[iz])] + end) + '\n'
				of.write(out)
	with open(global_out, 'w') as f:
		for iz in offset:
			f.write("%d\t%.3f\n" % (iz, offset[iz]))

if __name__ == "__main__":
	filename = "/afs/cern.ch/work/p/phansen/public/EcalTiming/round1/AlCaPhiSym-251252/ecalTiming-251252-0_numEvent5000000-corr.dat"
	calib = shiftCalib(filename);
	filename = "/afs/cern.ch/work/p/phansen/public/EcalTiming/round1/AlCaPhiSym-251562/ecalTiming-251562-0_numEvent5000000-corr.dat"
	calib = shiftCalib(filename);


