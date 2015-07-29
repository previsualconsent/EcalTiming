import ROOT
import  EcalTiming.EcalTiming.loadOldCalib as cal
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle
import sys,os
import shutil
import errno

def energyDiff(outdir, map1, map2, name1, name2):

	diffMap = cal.addCalib(map1, map2, -1, 1)
	cal.plot1d(diffMap, outdir,  "diff" + name2 + "_" + name1, -1, 1)
	cal.plot2d(diffMap, outdir,  "diffMap" + name2 + "_" + name1, -1, 1)
	ringdiff = cal.plotiRing(diffMap, outdir,  "iRing" + name2 + "_" + name1)
	return ringdiff

if __name__ == "__main__":
	customROOTstyle()
	ROOT.gROOT.SetBatch(True)
	file_pattern = sys.argv[1]
	dirname = sys.argv[2]

	dir, basename = os.path.split(file_pattern)
	dir = dir.split('/')
	print dir[-1:]
	outdir = '/'.join(dir[:-1]) + "/plots/" + dir[-1] + "/" + dirname +"/"
	outdir = os.path.normpath(outdir)

	def mkdir_p(path):
		try:
			os.makedirs(path)
		except OSError as exc: # Python >2.5
			if exc.errno == errno.EEXIST and os.path.isdir(path):
				pass
			else: raise

	mkdir_p(outdir)
	shutil.copy("plots/index.php", outdir)

	energies = ["0.0", "0.5", "1.0"]
	energies = ["0.0", "0.5", "1.0", "1.5", "2.0", "2.5"]

	files = [ file_pattern % en for en in energies ]

	maps =  [ cal.getCalibFromFile(file) for file in files ]

	mg = dict()
	mg[0]  = ("EB_iRing_err",ROOT.TMultiGraph())
	mg[-1] = ("EEM_iRing_err",ROOT.TMultiGraph())
	mg[1]  = ("EEP_iRing_err",ROOT.TMultiGraph())

	colors = [ROOT.kCyan, ROOT.kRed, ROOT.kBlue, ROOT.kGreen,
	      ROOT.kBlack]
	
	x1 = ROOT.gStyle.GetPadLeftMargin();
	x2 = 1 - ROOT.gStyle.GetPadRightMargin();
	y1 = ROOT.gStyle.GetPadBottomMargin();
	y2 = y1 + .1
	leg = ROOT.TLegend(x1,y1,x2,y2)
	leg.SetNColumns(4)
	for i in range(len(files) - 1):
		ringDiff = energyDiff(outdir, maps[i], maps[i+1], energies[i], energies[i+1])
		for j in ringDiff:
			g = ROOT.TGraphErrors(ringDiff[j])
			g.SetLineColor(colors[i])
			mg[j][1].Add(g)
		leg.AddEntry(g,energies[i+1] + " - " + energies[i])

	for name,g in mg.values():
		c = ROOT.TCanvas("c","c",1600,1200)
		g.Draw("ALP")
		g.GetXaxis().SetTitle("#eta Ring")
		g.GetYaxis().SetTitle("Average Time[ns]")
		leg.Draw()
		c.SaveAs(outdir + "/" +  name + ".png")

