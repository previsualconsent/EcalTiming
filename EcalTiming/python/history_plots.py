import ROOT
import  EcalTiming.EcalTiming.loadOldCalib as cal
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle, makePlotFolder
from EcalTiming.EcalTiming.csvDatabase import Database
import sys,os
import shutil
import errno
import numpy as np
import argparse
from datetime import datetime

colors = [
		ROOT.TColor.GetColor("#1f78b4"),
		ROOT.TColor.GetColor("#a6cee3"),
		ROOT.TColor.GetColor("#33a02c"),
		ROOT.TColor.GetColor("#b2df8a"),
		ROOT.TColor.GetColor("#e31a1c"),
		ROOT.TColor.GetColor("#fb9a99"),
		]
colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kOrange, ROOT.kGreen + 3, ROOT.kCyan - 3]
markers = [20, 24, 21, 25, 22, 26, 23, 27]
markers = [20, 21, 22, 23, 24, 25, 26, 27]

SubDet = ["EB+", "EB-", "EE+", "EE-"]
SubDetKey = [(0,1), (0,-1), 1, -1]
Sub2Key = dict(zip(SubDet, SubDetKey))
Key2Sub = dict(zip(SubDetKey, SubDet))
Key2Sub[0] = "EB"

iRingsEB = [ (0,1), (0,-1), (0,40), (0,-40), (0,80), (0,-80)]
iRingsEEM= [(-1, 5), (-1,15), (-1,25), (-1,35)]
iRingsEEP= [(1, 5), (1,15), (1,25), (1,35)]
iRings = iRingsEB + iRingsEEM + iRingsEEP

ringColumns = ( [ "EB_%d" % p[1] for p in iRingsEB] +
 		[ "EE-_%d" % p[1] for p in iRingsEEM] +
 		[ "EE+_%d" % p[1] for p in iRingsEEP])
iRings2Columns = dict( zip(iRings, ringColumns) )
Columns2iRings= dict( zip(ringColumns, iRings) )
ringColumns += [s + "_STD" for s in ringColumns]
db_time = Database("data/runsummary_270988_284068.dat", dialect = "space")
db_fills = Database("data/FillReport_1477414434155.xls", dialect = "excel-tab")

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

def plotAvePerMap(hist_name, db_ave, maps, names):

	nmaps = len(names)

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
	
	time = np.zeros(nmaps)
	
	failed = []
	for i in range(nmaps):
		try:
			print names[i],
			row = db_ave.get(names[i])
			ave = {Sub2Key[key]:row[key] for key in SubDet}
			stddev = {Sub2Key[key]:row[key + "_STD"] for key in SubDet}
			print "loaded from db",
		except KeyError:
			ave,stddev = cal.calcMean(maps[names[i]])
			if ave is None:
				print "failed"
				failed.append(i)
				continue
			else:
				row = {Key2Sub[key]:"%.5f" % ave[key] for key in ave}
				db_ave.set(names[i], row)
				row = {Key2Sub[key] + "_STD":"%.5f" % stddev[key] for key in stddev}
				db_ave.set(names[i], row)
				db_ave.setEntry(names[i], "TIMESTAMP", db_time.get(names[i], "STARTTIME"))
				db_ave.write()
		for k in aves:
			if k in ave:
				aves[k][1][i] = ave[k]
				sds[k][1][i] = stddev[k]

		time[i] = db_time.get(names[i], "STARTTIME")
		
		maxsd = max(sds[(0,-1)][1][i], sds[(0,1)][1][i], sds[-1][1][i], sds[1][1][i]) 
		minsd = min(sds[(0,-1)][1][i], sds[(0,1)][1][i], sds[-1][1][i], sds[1][1][i]) 
		if minsd > .3:
			if i not in failed:
				print "high sd",
				failed.append(i)
		print 


	for i in reversed(failed):
		nmaps -= 1
		if names[i] in maps:
			del maps[names[i]]
		names.pop(i)
		time = np.delete(time,i)
		for k in aves:
			aves[k][1] = np.delete(aves[k][1],i)
			sds[k][1]  = np.delete(sds[k][1],i)

	h = ROOT.TH1F("test","",1000,min(time),max(time))
	h.SetLineColor(0)
	h.SetFillColor(19)
	h.GetXaxis().SetTitle("")
	h.GetXaxis().SetTimeDisplay(1)
	h.GetXaxis().SetTimeOffset(0)
	h.GetXaxis().SetTimeFormat("%m-%d")
	h.GetYaxis().SetTitle("Average Time[ns]")

	x = np.linspace(0,1,nmaps)
	x = time

	if len(names) < 10:
		binnames = names
	else:
		binnames = names[::len(names)/10]
	
	binnames = names

	#labelBins(h, x, names,  binnames)
	#lines = getLines(h, x, names, binnames)
	lines =[]

	print len(x), len(aves[1])
	plot(h, x, aves, aves.keys(), "ave_" + hist_name, -.2, 0.7, None, None, lines)

	h.GetYaxis().SetTitle("Standard Deviation [ns]")
	plot(h, x, sds, sds.keys(), "stddev_" + hist_name, 0, 1, None, None, lines)

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

def plotRingAverPerMap(hist_name, db_ring, maps, names):

	nmaps = len(names)

	aves = dict()
	sds = dict()
	leg_format = "{subdet}: iRing={iring:+d}"
	for key in iRings:
		leg_name = leg_format.format(subdet=Key2Sub[key[0]], iring = key[1])
		aves[key] = [ leg_name, np.zeros(nmaps, dtype=float)]
		sds[key] = [ leg_name, np.zeros(nmaps, dtype=float)]
	
	time = np.zeros(nmaps)
	failed = []
	for i in range(nmaps):
		try:
			print names[i],
			row = db_ring.get(names[i])
			ave = {Columns2iRings[key]:row[key] for key in Columns2iRings}
			stddev = {Columns2iRings[key]:row[key + "_STD"] for key in Columns2iRings}
			print "loaded from db"
		except KeyError:
			ave,stddev = cal.calcMeanByiRing(maps[names[i]], iRings)
			if ave is None:
				print "failed"
				failed.append(i)
				continue
			else:
				try:
					row = {iRings2Columns[key]:"%.5f" % ave[key] for key in aves}
					db_ring.set(names[i], row)
					row = {iRings2Columns[key] + "_STD":"%.5f" % stddev[key] for key in sds}
					db_ring.set(names[i], row)
					db_ring.setEntry(names[i], "TIMESTAMP", db_time.get(names[i], "STARTTIME"))
					db_ring.write()
				except KeyError as e:
					print "failed"
					failed.append(i)
					continue
			print

		time[i] = db_time.get(names[i], "STARTTIME")
		for k in aves:
			if k in ave:
				aves[k][1][i] = ave[k]
				sds[k][1][i] = stddev[k]
	
	for i in reversed(failed):
		nmaps -= 1
		if names[i] in maps:
			del maps[names[i]]
		names.pop(i)
		time = np.delete(time,i)
		for k in aves:
			aves[k][1] = np.delete(aves[k][1],i)
			sds[k][1]  = np.delete(sds[k][1],i)

	
	h = ROOT.TH1F("test","",1000,min(time), max(time))
	h.SetLineColor(0)
	h.SetFillColor(19)
	x = np.linspace(0,1,nmaps)
	x = time
	h.GetXaxis().SetTitle("")
	h.GetYaxis().SetTitle("Average Time[ns]")

	if len(names) < 10:
		binnames = names
	else:
		binnames = names[::len(names)/10]
	binnames = names
	#labelBins(h, x, names, binnames)
	lines = getLines(h, x, names, binnames)
	lines = []

	plot(h, x, aves, iRingsEB, "ave_EB_iRing"  , -1.5, .7, None, None, lines)
	plot(h, x, aves, iRingsEEM, "ave_EEM_iRing", -1.5, .7, None, None, lines)
	plot(h, x, aves, iRingsEEP, "ave_EEP_iRing", -1.5, .7, None, None, lines)

	k0 = (0,1)
	for k in iRingsEB:
		if k != k0:
			aves[k][1] -= aves[k0][1]
	aves[k0][1].fill(0)

	k0 = (1,5)
	for k in iRingsEEP:
		if k != k0:
			aves[k][1] -= aves[k0][1]
	aves[k0][1].fill(0)

	k0 = (-1,5)
	for k in iRingsEEM:
		if k != k0:
			aves[k][1] -= aves[k0][1]
	aves[k0][1].fill(0)
	
	h.GetYaxis().SetTitle("Average Time Relative to iRing=1 [ns]")
	plot(h, x, aves, iRingsEB, "ave_EB_iRing_rel"  , -.7, .7, None, None, lines)

	h.GetYaxis().SetTitle("Average Time Relative to iRing=5 [ns]")
	plot(h, x, aves, iRingsEEM, "ave_EEM_iRing_rel", -.7, .7, None, None, lines)

	h.GetYaxis().SetTitle("Average Time Relative to iRing=5 [ns]")
	plot(h, x, aves, iRingsEEP, "ave_EEP_iRing_rel", -.7, .7, None, None, lines)

	h.GetYaxis().SetTitle("Standard Deviation [ns]")
	plot(h, x, sds, iRingsEB , "stddev_EB_iRing",  0, 1, None, None, lines)
	plot(h, x, sds, iRingsEEM, "stddev_EEM_iRing", 0, 1, None, None, lines)
	plot(h, x, sds, iRingsEEP, "stddev_EEP_iRing", 0, 1, None, None, lines)

def plot(h, x, graphs, keys, name, min_y, max_y, box_x1, box_x2, lines):
	c = ROOT.TCanvas("c","c",1000,500)
	h.SetTitle("Prompt Reco Ecal Timing [2016]")

	h.GetXaxis().SetTimeDisplay(1)
	h.GetXaxis().SetTimeOffset(0)
	h.GetXaxis().SetTimeFormat("%d/%m")
	h.GetXaxis().SetTitle("Run Start Time")
	h.GetXaxis().SetNdivisions(40413)
	
	h.SetMinimum(min_y)
	h.SetMaximum(max_y)
	h.Draw()
	h.SetFillStyle(3004)
	h.SetFillColor(ROOT.kBlack)

	c.SetBottomMargin(.1)
	c.SetLeftMargin(.1)
	c.SetRightMargin(.03)
	c.SetGridx()
	c.SetGridy()
	c.SetHighLightColor(3)
	h.GetYaxis().SetTitleOffset(1)

	x1 = c.GetLeftMargin();
	x2 = 1 - c.GetRightMargin();
	y2 = 1 - c.GetTopMargin();
	y1 = y2 - .1

	x2 = x1 + 800./c.GetWw()

	leg = ROOT.TLegend(0.32, 0.57, 0.45, 0.90)
	#leg.SetNColumns(len(keys) + 1)

	#added boxes
	#leg.AddEntry(h,"Bon","f")
	#boxes = drawBoxes(h, box_x1,box_x2,min_y,max_y)
	
	
	#line = ROOT.TLine(0,0,1,0)
	#line.Draw()
	#linestorage = []
	#for row in db_fills.db:
	#	#print db_fills.get(row, "Begin Time")
	#	linex = ( datetime.strptime(db_fills.get(row, "Begin Time"), "%Y.%m.%d %H:%M:%S") - datetime.utcfromtimestamp(0)).total_seconds()
	#	if linex > max(x): continue
	#	linestorage.append(ROOT.TLine(linex,h.GetMinimum(),linex,h.GetMaximum()))
	#	linestorage[-1].Draw()

	ci = 0
	mg_ave = ROOT.TMultiGraph()
	for key in keys:
		leg_name,ave = graphs[key]
		g = ROOT.TGraph(len(x),x,ave)
		g.SetLineColor(colors[ci % len(colors)])
		g.SetMarkerColor(colors[ci % len(colors)])
		g.SetMarkerStyle(markers[ci % len(markers)])
		g.SetMarkerSize(1)
		g.SetLineWidth(2)
		mg_ave.Add(g)
		leg.AddEntry(g,leg_name,"p")
		ci += 1
	mg_ave.Draw("p")
	leg.Draw()
	c.SaveAs(outdir + "/" +  name + ".png")
	c.SaveAs(outdir + "/" +  name + ".pdf")
	c.SaveAs(outdir + "/" +  name + ".C")

if __name__ == "__main__":
	customROOTstyle()
	ROOT.gROOT.SetBatch(True)

	parser = argparse.ArgumentParser()
	parser.add_argument("filepattern")
	parser.add_argument("outdir")
	parser.add_argument("dbfile_root")
	parser.add_argument("subs", nargs="+")
	args = parser.parse_args()

	file_pattern = args.filepattern
	outdir = args.outdir
	subs =  args.subs

	makePlotFolder(outdir)

	db_ave = Database(args.dbfile_root + "_ave.dat", headers = ["RUN", "TIMESTAMP", "EB+", "EB-", "EE+", "EE-", "EB+_STD", "EB-_STD", "EE+_STD", "EE-_STD"])

	db_ring = Database(args.dbfile_root + "_iRing.dat", headers = ["RUN", "TIMESTAMP"] + ringColumns )

	load_subs = [s for s in subs if (s not in db_ave.db) or (s not in db_ring.db)]

	print "loading maps"
	maps =  { s:cal.getCalibFromFile(file_pattern % s ) for s in load_subs }
	#print "loading errors"
	#maps_err =  [ cal.getErrorFromFile(file) for file in files ]

	plotRingAverPerMap("PerRuniRing", db_ring, maps, subs)
	db_ring.write()
	plotAvePerMap("PerRun", db_ave, maps, subs)
	db_ave.write()
