import ROOT
import  EcalTiming.EcalTiming.loadOldCalib as cal
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle, makePlotFolder
import sys,os
import shutil
import errno
import numpy as np

colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kOrange, ROOT.kMagenta, ROOT.kOrange - 3, ROOT.kYellow -2, ROOT.kGreen - 3, ROOT.kCyan - 3]
markers = [20, 24, 21, 25, 22, 26, 23, 27]
markers = [20, 21, 22, 23, 24, 25, 26, 27]


IOVS = [
		"272012", 
		"273158",
		"274088",
		"274159",
		"274251",
		"274954",
		"274968",
		"275345",
		"275834",
		"276217",
		"276317",
		"276831",
		"277792",
		"278017",
		"278310",
		"278770",
		"279479",
		"279653",
		"279588",
		"279667",
		"279844",
		"279887",
		"280016",
		"280017",
		"281613",
		"281641",
		"281707",
		"282663",
		]
def mapDiff(outdir, map1, map2, name1, name2, errs=[]):

	diffMap = cal.addCalib(map1, map2, -1, 1)
	
	ROOT.gStyle.SetOptStat(1100)
	if errs:
		resMap = cal.divideCalib(map1, errs)
		cal.plot1d(resMap,outdir, "resmap" + name2 + "_" + name1, -.5, .5, xtitle="diff/timeError")
	cal.plot1d(diffMap, outdir,  "diff" + name2 + "_" + name1, -.5, .5)
	ROOT.gStyle.SetOptStat(0)
	cal.plot2d(diffMap, outdir,  "diffMap" + name2 + "_" + name1, -.5, .5)
	ringdiff = cal.plotiRing(diffMap, outdir,  "iRing" + name2 + "_" + name1)
	return ringdiff

def plotAvePerMap(hist_name, maps, names):

	nmaps = len(maps)
	if nmaps != len(names):
		print "LENGTH MISMATCH"
		return

	Bon_start = ["251244", "254790", "256630"] 
	Bon_end   = ["254232", "254914", "259891"]
	aves = dict()
	#aves[0]      = ("EB_ave_"  + hist_name, "EB",  np.zeros(nmaps))
	aves[(0,-1)] = ["EB-", np.zeros(nmaps)]
	aves[(0,1)]  = ["EB+", np.zeros(nmaps)]
	aves[-1]     = ["EE-", np.zeros(nmaps)]
	aves[1]      = ["EE+", np.zeros(nmaps)]
	sds = dict()
	#sds[0]      = ("EB_stddev_"  + hist_name, "EB",  np.zeros(nmaps))
	sds[(0,-1)] = ["EB-", np.zeros(nmaps)]
	sds[(0,1)]  = ["EB+", np.zeros(nmaps)]
	sds[-1]     = ["EE-", np.zeros(nmaps)]
	sds[1]      = ["EE+", np.zeros(nmaps)]
	
	failed = []
	print "HISTORY RUN EB- EB+ EE- EE+ HIGH_SD"
	for i in range(nmaps):
		print names[i]
		ave,stddev = cal.calcMean(maps[i])
		if ave is None:
			failed.append(i)
			continue
		for k in aves:
			if k in ave:
				aves[k][1][i] = ave[k]
				sds[k][1][i] = stddev[k]
		
		maxsd = max(stddev[(0,-1)], stddev[(0,1)], stddev[-1], stddev[1]) 
		minsd = min(stddev[(0,-1)], stddev[(0,1)], stddev[-1], stddev[1]) 
		print "HISTORY", names[i], ave[(0,-1)], ave[(0,1)], ave[-1], ave[1],
		if minsd > .3:
			print "HIGH_SD"
			if i not in failed:
				failed.append(i)
		else:
			print "NORM_SD"


	for i in reversed(failed):
		nmaps -= 1
		names.pop(i)
		maps.pop(i)
		for k in aves:
			aves[k][1] = np.delete(aves[k][1],i)
			sds[k][1]  = np.delete(sds[k][1],i)

	
	h = ROOT.TH1F("test","",1000,-.02,1.02)
	h.SetLineColor(0)
	h.SetFillColor(19)
	h.GetXaxis().SetTitle("")
	h.GetYaxis().SetTitle("Average Time[ns]")

	x = np.linspace(0,1,nmaps)

	box_x1, box_x2 = getBoxXs(h, x, names, Bon_start, Bon_end)

	if len(names) < 10:
		binnames = names
	else:
		binnames = names[::len(names)/10]
	
	binnames = names

	labelBins(h, x, names,  binnames)
	lines = getLines(h, x, names, binnames)

	plot(h, x, aves, aves.keys(), "ave_" + hist_name, -1.5, .7, box_x1, box_x2, lines)

	h.GetYaxis().SetTitle("Standard Deviation [ns]")
	plot(h, x, sds, sds.keys(), "stddev_" + hist_name, 0, 2, box_x1, box_x2, lines)

def plotPullPerMap(hist_name, maps, errors, names):

	nmaps = len(maps) - 1
	if nmaps != len(names):
		print "LENGTH MISMATCH"
		return

	Bon_start = ["251244", "254790", "256630"] 
	Bon_end   = ["254232", "254914", "256867"]
	aves = dict()
	#aves[0]      = ("EB_ave_"  + hist_name, "EB",  np.zeros(nmaps))
	aves[(0,-1)] = ("EB-", np.zeros(nmaps))
	aves[(0,1)]  = ("EB+", np.zeros(nmaps))
	aves[-1]     = ("EE-", np.zeros(nmaps))
	aves[1]      = ("EE+", np.zeros(nmaps))
	sds = dict()
	#sds[0]      = ("EB_stddev_"  + hist_name, "EB",  np.zeros(nmaps))
	sds[(0,-1)] = ("EB-", np.zeros(nmaps))
	sds[(0,1)]  = ("EB+", np.zeros(nmaps))
	sds[-1]     = ("EE-", np.zeros(nmaps))
	sds[1]      = ("EE+", np.zeros(nmaps))

	skews = dict()
	skews[(0,-1)] = ("EB-", np.zeros(nmaps))
	skews[(0,1)]  = ("EB+", np.zeros(nmaps))
	skews[-1]     = ("EE-", np.zeros(nmaps))
	skews[1]      = ("EE+", np.zeros(nmaps))
	
	for i in range(nmaps):
		print names[i]
		ave,stddev,skew = cal.calcPull(maps[i], maps[i+1], errors[i])
		for k in aves:
			if k in ave:
				aves[k][1][i] = ave[k]
				sds[k][1][i] = stddev[k]
				skews[k][1][i] = skew[k]

	
	h = ROOT.TH1F("test","",1000,-.02,1.02)
	h.SetLineColor(0)
	h.SetFillColor(19)
	h.GetXaxis().SetTitle("")
	h.GetYaxis().SetTitle("Average Time[ns]")

	x = np.linspace(0,1,nmaps)

	box_x1, box_x2 = getBoxXs(h, x, names, Bon_start, Bon_end)

	if len(names) < 10:
		binnames = names
	else:
		binnames = names[::len(names)/10]

	binnames = names
	labelBins(h, x, names,  binnames)
	lines = getLines(h, x, names, binnames)

	plot(h, x, aves, aves.keys(), "ave_" + hist_name, -1, 1, box_x1, box_x2, lines)

	h.GetYaxis().SetTitle("Standard Deviation [ns]")
	plot(h, x, sds, sds.keys(), "stddev_" + hist_name, 0, 10, box_x1, box_x2, lines)

	h.GetYaxis().SetTitle("Skew")
	plot(h, x, skews, skews.keys(), "skew_" + hist_name, -200, 200, box_x1, box_x2, lines)

def labelBins(h, x, names, binnames):
	binnames = IOVS
	for i in range(len(names)):
		bin = h.FindBin(x[i])
		if names[i] in binnames:
			h.GetXaxis().SetBinLabel(bin,names[i])

def labelBinsDates(h, x, names, binnames):
	binnames = {
			"271036":"2016A-v1",
			"272011":"2016B-v1",
			"273158":"2016B-v2",
			"275657":"2016C-v2",
			"276317":"2016D-v2",
			"276831":"2016E-v2",
			"277932":"2016F-v1",
			"278820":"2016G-v1",
			}

	bindates = {
			"271036":"",
			"272011":"2016.04.29",
			"273158":"2016.05.11",
			"275657":"2016.06.23",
			"276317":"2016.07.04",
			"276831":"2016.07.16",
			"277932":"2016.07.31",
			"278820":"2016.08.14",
			}
	for i in range(len(names)):
		bin = h.FindBin(x[i])
		if names[i] in binnames:
			h.GetXaxis().SetBinLabel(bin,binnames[names[i]])
			h.GetXaxis().SetBinLabel(bin+7,bindates[names[i]])

def getLines(h, x, names, binnames):
	#binnames = [
	#		"271036",
	#		"272011",
	#		"273158",
	#		"275657",
	#		"276317",
	#		"276831",
	#		"277932",
	#		"278820",
	#		]
	binnames = IOVS
	lines = []
	for i in range(len(names)):
		bin = h.FindBin(x[i])
		if names[i] in binnames:
			lines.append(h.GetBinCenter(bin))
	return lines

def getBoxXs(h, x, names, Bon_start, Bon_end):
	box_x1 = [0]*len(Bon_start)
	box_x2 = [0]*len(Bon_start)
	for i in range(len(names)):
		bin = h.FindBin(x[i])
		if names[i] in Bon_start:
			box_x1[Bon_start.index(names[i])] = x[i]
		if names[i] in Bon_end:
			box_x2[Bon_end.index(names[i])] = x[i]
	return (box_x1, box_x2)

def drawBoxes(h, x1, x2, y1,y2):
		boxes = []
		for bi in range(len(x1)):
			b =  ROOT.TBox(x1[bi],y1,x2[bi],y2) 
			b.SetFillStyle(h.GetFillStyle())
			b.SetFillColor(h.GetFillColor())
			b.Draw()
			boxes.append(b)
		return boxes

def plotRingAverPerMap(hist_name, maps, names):

	nmaps = len(maps)
	if nmaps != len(names):
		print "LENGTH MISMATCH"
		return

	Bon_start = ["251244", "254790", "256630"] 
	Bon_end   = ["254232", "254914", "259891"]

	iRingsEB = [ (0,-80), (0,-1), (0,1), (0,80)]
	iRingsEEM= [(-1, 5), (-1,15), (-1,25), (-1,35)]
	iRingsEEP= [(1, 5), (1,15), (1,25), (1,35)]

	iRings = iRingsEB + iRingsEEM + iRingsEEP
	aves = dict()
	sds = dict()
	for key in iRings:
		aves[key] = [ "(%d,%d)" % key, np.zeros(nmaps)]
		sds[key] = [ "(%d,%d)" % key, np.zeros(nmaps)]
	
	failed = []
	for i in range(nmaps):
		print names[i],
		ave,stddev = cal.calcMeanByiRing(maps[i], iRings)
		if ave is None:
			print "failed"
			failed.append(i)
			continue
		print
		for k in aves:
			if k in ave:
				aves[k][1][i] = ave[k]
				sds[k][1][i] = stddev[k]

	for i in reversed(failed):
		nmaps -= 1
		names.pop(i)
		maps.pop(i)
		for k in aves:
			aves[k][1] = np.delete(aves[k][1],i)
			sds[k][1]  = np.delete(sds[k][1],i)

	
	h = ROOT.TH1F("test","",1000,-.02,1.02)
	h.SetLineColor(0)
	h.SetFillColor(19)
	x = np.linspace(0,1,nmaps)
	h.SetTitle("Offline Ecal Timing ")
	h.GetXaxis().SetTitle("")
	h.GetYaxis().SetTitle("Average Time[ns]")

	box_x1, box_x2 = getBoxXs(h, x, names, Bon_start, Bon_end)

	if len(names) < 10:
		binnames = names
	else:
		binnames = names[::len(names)/10]
	binnames = names
	labelBins(h, x, names, binnames)
	lines = getLines(h, x, names, binnames)

	plot(h, x, aves, iRingsEB, "ave_EB_iRing"  , -1.5, .7, box_x1, box_x2, lines)
	plot(h, x, aves, iRingsEEM, "ave_EEM_iRing", -1.5, .7, box_x1, box_x2, lines)
	plot(h, x, aves, iRingsEEP, "ave_EEP_iRing", -1.5, .7, box_x1, box_x2, lines)

	h.GetYaxis().SetTitle("Standard Deviation [ns]")
	plot(h, x, sds, iRingsEB , "stddev_EB_iRing",  0, 2, box_x1, box_x2, lines)
	plot(h, x, sds, iRingsEEM, "stddev_EEM_iRing", 0, 2, box_x1, box_x2, lines)
	plot(h, x, sds, iRingsEEP, "stddev_EEP_iRing", 0, 2, box_x1, box_x2, lines)

def plot(h, x, graphs, keys, name, min_y, max_y, box_x1, box_x2, lines):
	c = ROOT.TCanvas("c","c",6000,800)
	h.SetTitle("Offline Ecal Timing ")
	h.SetMinimum(min_y)
	h.SetMaximum(max_y)
	h.Draw()
	h.SetFillStyle(3004)
	h.SetFillColor(ROOT.kBlack)

	c.SetBottomMargin(.2)
	c.SetLeftMargin(.03)
	c.SetRightMargin(.03)
	h.GetYaxis().SetTitleOffset(.3)

	x1 = c.GetLeftMargin();
	x2 = 1 - c.GetRightMargin();
	y2 = 1 - c.GetTopMargin();
	y1 = y2 - .1

	x2 = x1 + 800./c.GetWw()

	leg = ROOT.TLegend(x1,y1,x2,y2)
	leg.SetNColumns(len(keys) + 1)

	#added boxes
	#leg.AddEntry(h,"Bon","f")
	#boxes = drawBoxes(h, box_x1,box_x2,min_y,max_y)
	
	line = ROOT.TLine(0,0,1,0)
	line.Draw()
	linestorage = []
	for linex in lines:
		linestorage.append(ROOT.TLine(linex,h.GetMinimum(),linex,h.GetMaximum()))
		linestorage[-1].Draw()

	ci = 0
	mg_ave = ROOT.TMultiGraph()
	for key in keys:
		leg_name,ave = graphs[key]
		g = ROOT.TGraph(len(x),x,ave)
		g.SetLineColor(colors[ci % len(colors)])
		g.SetMarkerColor(colors[ci % len(colors)])
		g.SetMarkerStyle(markers[ci % len(markers)])
		g.SetMarkerSize(1.5)
		g.SetLineWidth(3)
		mg_ave.Add(g)
		leg.AddEntry(g,leg_name,"lp")
		ci += 1
	leg.Draw()
	mg_ave.Draw("LP")
	c.SaveAs(outdir + "/" +  name + ".png")
	c.SaveAs(outdir + "/" +  name + ".pdf")
	c.SaveAs(outdir + "/" +  name + ".C")

def listDiff(hist_name, maps1, maps2, names1, names2, errs=[]):
	mg = dict()
	mg[0]  = ("EB_" + hist_name,ROOT.TMultiGraph())
	mg[-1] = ("EEM_" + hist_name,ROOT.TMultiGraph())
	mg[1]  = ("EEP_" + hist_name,ROOT.TMultiGraph())

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

	#dir, basename = os.path.split(file_pattern)
	#dir = dir.split('/')
	#print dir[-1:]
	##outdir = '/'.join(dir) + "/plots/" + "/" + sys.argv[2] + "/"
	#outdir = '/'.join(dir[:-1]) + "/plots/" + "/" + sys.argv[2] + "/"
	#outdir = os.path.normpath(outdir)

	outdir = sys.argv[2]

	makePlotFolder(outdir)

	subs =  sys.argv[3:]
	files = [ file_pattern % s for s in subs ]
	print "loading maps"
	maps =  [ cal.getCalibFromFile(file) for file in files ]
	#print "loading errors"
	#maps_err =  [ cal.getErrorFromFile(file) for file in files ]
	
	print outdir
	#plotRingAverPerMap("PerRuniRing", maps, subs)
	#plotAvePerMap("PerRun", maps, subs)
   #do diff each step
	listDiff( sys.argv[2], maps[:-1], maps[1:], subs[:-1], subs[1:])
   #do diff with respect to first
	#names = [ s.split('/')[0] for s in subs]
	#listDiff(sys.argv[2] , maps[:1]*(len(maps)-1), maps[1:], names[:1]*(len(maps) -1), names[1:], errs=maps_err[:-1])

