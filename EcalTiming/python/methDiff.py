import ROOT
import  EcalTiming.EcalTiming.loadOldCalib as cal
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle
import sys,os
import shutil
import errno

def mapDiff(outdir, map1, map2, name1, name2, errs=[]):

	diffMap = cal.addCalib(map1, map2, -1, 1)
	
	ROOT.gStyle.SetOptStat(1100)
	if errs:
		resMap = cal.divideCalib(map1, errs)
		cal.plot1d(resMap,outdir, "resmap" + name2 + "_" + name1, -2, 2, xtitle="diff/timeError")
	cal.plot1d(diffMap, outdir,  "diff" + name2 + "_" + name1, -.4, .4)
	ROOT.gStyle.SetOptStat(0)
	cal.plot2d(diffMap, outdir,  "diffMap" + name2 + "_" + name1, -.4, .4)
	ringdiff = cal.plotiRing(diffMap, outdir,  "iRing" + name2 + "_" + name1)
	return ringdiff

def listDiff(hist_name, maps1, maps2, names1, names2, errs=[]):
	mg = dict()
	mg[0]  = ("EB_" + hist_name,ROOT.TMultiGraph())
	mg[-1] = ("EEM_" + hist_name,ROOT.TMultiGraph())
	mg[1]  = ("EEP_" + hist_name,ROOT.TMultiGraph())

	colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kCyan, ROOT.kMagenta]
	
	x1 = ROOT.gStyle.GetPadLeftMargin();
	x2 = 1 - ROOT.gStyle.GetPadRightMargin();
	y1 = ROOT.gStyle.GetPadBottomMargin();
	y2 = y1 + .1
	leg = ROOT.TLegend(x1,y1,x2,y2)
	leg.SetNColumns(4)
	nmaps = len(maps1)
	if nmaps != len(maps2) or nmaps != len(names1) or nmaps!= len(names2):
		print "LENGTH MISMATCH"
		return

	for i in range(nmaps):
		ringDiff = mapDiff(outdir, maps1[i], maps2[i], names1[i], names2[i], errs=errs[i] if errs else [])
		for j in ringDiff:
			g = ROOT.TGraphErrors(ringDiff[j])
			g.SetLineColor(colors[i % len(colors)] )
			mg[j][1].Add(g)
		leg.AddEntry(g,names2[i] + " - " + names1[i])

	for name,g in mg.values():
		c = ROOT.TCanvas("c","c",1600,1200)
		g.Draw("ALP")
		g.GetXaxis().SetTitle("#eta Ring")
		g.GetYaxis().SetTitle("Average Time[ns]")
		leg.Draw()
		c.SaveAs(outdir + "/" +  name + ".png")

if __name__ == "__main__":
	customROOTstyle()
	ROOT.gROOT.SetBatch(True)
	file_pattern = sys.argv[1]

	dir, basename = os.path.split(file_pattern)
	dir = dir.split('/')
	print dir[-2:]
	outdir = '/'.join(dir[:-2]) + "/plots/" + "/" + sys.argv[2] + "/"
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

	subs =  sys.argv[3:]
	files = [ file_pattern % s for s in subs ]
	maps =  [ cal.getCalibFromFile(file) for file in files ]
	maps_err =  [ cal.getErrorFromFile(file) for file in files ]
	
	print files
	print outdir
	#listDiff( sys.argv[2], maps[:-1], maps[1:], subs[:-1], subs[1:], errs=maps_err[:-1])
	listDiff(sys.argv[2], maps[:1]*(len(maps)-1), maps[1:], subs[:1]*(len(maps) -1), subs[1:], errs=maps_err[:-1])

