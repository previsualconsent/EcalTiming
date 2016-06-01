import ROOT
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle, customPalette
import math

import os
import sys
import errno
import shutil


detectors = {-1: "EEM", 0: "EB", 1: "EEP"}


def float2name(x):
	return ("%.1f" % x).replace('.', '_')


def initMap(name, title, iz):
	if iz == 0:
		h = ROOT.TProfile2D("EB_" + name, title, 360, 1, 361, 171, -85, 86)
		xtitle = "i#phi"
		ytitle = "i#eta"
	elif iz == -1:
		h = ROOT.TProfile2D("EEM_" + name, title, 100, 1, 101, 100, 1, 101)
		xtitle = "ix"
		ytitle = "iy"
	elif iz == 1:
		h = ROOT.TProfile2D("EEP_" + name, title, 100, 1, 101, 100, 1, 101)
		xtitle = "ix"
		ytitle = "iy"
	else:
		print "bad iz value", iz
		return None
	h.SetXTitle(xtitle)
	h.SetYTitle(ytitle)
	return h


def inittime1d(name, title, iz, low=-10, hi=10):
	if iz == 0:
		det = "EB_"
	elif iz == -1:
		det = "EEM_"
	elif iz == 1:
		det = "EEP_"
	else:
		#print "bad iz value", iz
		det = str(iz)
	h = ROOT.TH1F(det + name, title, 50, low, hi)
	h.SetXTitle("Time [ns]")
	h.SetYTitle("Events")
	return h


def initiRing(name, title, iz, xtitle="iRing", ytitle="Mean Time [ns]"):
	if iz == 0:
		h = ROOT.TProfile("EB_" + name, title, 171, -85, 86)
	elif iz == -1:
		h = ROOT.TProfile("EEM_" + name, title, 39, 0, 39)
	elif iz == 1:
		h = ROOT.TProfile("EEP_" + name, title, 39, 0, 39)
	else:
		print "bad iz value", iz
		return None
	h.SetXTitle(xtitle)
	h.SetYTitle(ytitle)
	return h

def initEvsT(name, title, iz):
	if iz == 0:
		det = "EB" 
	elif iz == -1:
		det = "EEM" 
	elif iz == 1:
		det = "EEP" 
	else:
		print "bad iz value", iz
		return None
	h = ROOT.TH2F(det + name, title, 50,0,20,100,-10,10) 
	h.SetXTitle("Energy [GeV]")
	h.SetYTitle("Time [ns]")
	return h

def initHists(prefix,hist_dict, init_func, key, name, title,**kwargs):
	if key in hist_dict:
		return
	iz = key
	hist_dict[key] = init_func(prefix + '_' + name, title, iz, **kwargs)

def addFitToPlot(h,outfilename):
	c = ROOT.TCanvas("c","c",1600,1200)
	fit = ROOT.TF1("gaus","gaus")
	h.Fit(fit, "Q")
	mu = fit.GetParameter(1)
	sigma = fit.GetParameter(2)
	label = ROOT.TPaveText(.5, .7, .9, .9, "NDC")
	label.AddText("#mu = %.3f" % mu)
	label.AddText("#sigma = %.3f" % sigma)
	label.Draw()
	c.SaveAs(outfilename)
	return mu,sigma


def plotMaps(tree, outdir, prefix=""):
	low = -1
	hi = 1
	# dictionaries to store histograms
	time = dict()
	time_rel2012 = dict()
	timeError = dict()
	timeError1d = dict()
	stdDev = dict()
	occupancy = dict()
	energy = dict()
	iRing = dict()
	iRingError = dict()
	time1d = dict()
	EvsT = dict()

	CCU = dict()
	CCU_maps = dict()
	CCU_err_maps = dict()
	elec_map = dict()
	counter = 0

	print "Found", tree.GetEntries(), "entries"
	if tree.GetEntries() == 0: sys.exit(-1)
	
	offset = dict()
	for iz in detectors:
		tree.Draw("time>>temp%d(50,-5,5)" % iz,"iz == %d && num != 0" % iz)
		h = ROOT.gDirectory.FindObject("temp%d" % iz)
		offset[iz],__ = addFitToPlot(h,outdir + '/' + detectors[iz] + '_' + prefix + "_1d_noffset.png")

	from EcalTiming.EcalTiming.loadOldCalib import getCalib
	oldCalib = getCalib()

	for event in tree:
		if not counter % (tree.GetEntries()/10): print counter, '/', tree.GetEntries()
		counter += 1
		if event.num == 0: continue

		# make dictionary key
		if type(event.iz) == type("s"):
			iz = ord(event.iz)
			if iz == 255: iz = -1
		else:
			iz = event.iz
		key = iz
		if math.isnan(event.time): 
			print "Found nan", event.rawid, event.ix, event.iy, iz, event.num
			continue
		# initialize histograms (if they haven't been made yet
		initHists(prefix,time, initMap, key, "time", "Time [ns]")
		initHists(prefix,time_rel2012, initMap, key, "time_rel2012", "Time - old calib [ns]")
		initHists(prefix,timeError, initMap, key, "timeError", "Time Error[ns]")
		initHists(prefix,timeError1d, inittime1d, key, "timeError1d", "Time Error Test [ns]", low=0, hi=.2)
		initHists(prefix,stdDev, initMap, key, "stdDev", "Std Dev [ns]")
		initHists(prefix,time1d, inittime1d, key, "time1d", "time1d", low=low, hi=hi)

		initHists(prefix,occupancy, initMap, key, "occupancy", "Occupancy")
		initHists(prefix,energy, initMap, key, "energy", "Energy [GeV]")
		initHists(prefix,iRing, initiRing, key, "iRing", "iRing")
		initHists(prefix,iRingError, initiRing, key, "iRingError", "iRingError", xtitle="iRing", ytitle="Mean Time Error [ns]")
		initHists(prefix,EvsT, initEvsT, key, "EvsT", "EvsT")

		initHists(prefix,CCU, inittime1d, (event.elecID), "ccu_time", " CCU Time [ns]")
		initHists(prefix,CCU_maps, initMap, key, "ccu_time_map", "CCU Map [ns]")
		initHists(prefix,CCU_err_maps, initMap, key, "ccu_timeError_map", "CCU Error Map [ns]")
		
		elec_map[( event.ix, event.iy, iz)] = event.elecID
		
		# fill histograms
		if iz == 0:
			x = event.iy
			y = event.ix
		else:
			x = event.ix
			y = event.iy

		
		t = event.time - offset[iz]

		time[key].Fill(x, y, t)
		timeError[key].Fill(x, y, event.timeError)
		timeError1d[key].Fill(event.timeError)
		stdDev[key].Fill(x, y, event.timeError  * math.sqrt(event.num))
		time1d[key].Fill(t)

		occupancy[key].Fill(x, y, event.num)
		energy[key].Fill(x, y, event.energy)
		EvsT[key].Fill(event.energy, t)
		iRing[key].Fill(event.iRing, t)
		iRingError[key].Fill(event.iRing, event.timeError)

		CCU[event.elecID].Fill(t)

		if event.rawid in oldCalib:
			time_rel2012[key].Fill(x,y, t - oldCalib[event.rawid])
		else:
			print "Rawid not found", event.rawid 


	for ix,iy,iz in elec_map:
		if iz == 0:
			x = iy
			y = ix
		else:
			x = ix
			y = iy
		CCU_maps[iz].Fill(x,y,CCU[elec_map[(ix,iy,iz)]].GetMean())
		CCU_err_maps[iz].Fill(x,y,CCU[elec_map[(ix,iy,iz)]].GetStdDev())

	c = ROOT.TCanvas("c","c",1600,1200)
	for key in CCU_maps:
		CCU_maps[key].SetAxisRange(low,hi, "Z")
		CCU_maps[key].SetZTitle("[ns]")
		CCU_maps[key].Draw("colz")
		c.SaveAs(outdir + "/" + CCU_maps[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	for key in CCU_err_maps:
		CCU_err_maps[key].SetAxisRange(0, 2, "Z")
		CCU_err_maps[key].SetZTitle("[ns]")
		CCU_err_maps[key].Draw("colz")
		c.SaveAs(outdir + "/" + CCU_err_maps[key].GetName() + ".png")
		
	c = ROOT.TCanvas("c","c",1600,1200)
	for key in time:
		time[key].SetAxisRange(-10, 10, "Z")
		time[key].SetZTitle("[ns]")
		time[key].Draw("colz")
		c.SaveAs(outdir + "/" + time[key].GetName() + ".10.png")
		time[key].SetAxisRange(-5,5,"Z")
		time[key].Draw("colz")
		c.SaveAs(outdir + "/" + time[key].GetName() + ".5.png")
		time[key].SetAxisRange(low,hi,"Z")
		time[key].Draw("colz")
		c.SaveAs(outdir + "/" + time[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	for key in time_rel2012:
		time_rel2012[key].SetAxisRange(-10, 10, "Z")
		time_rel2012[key].SetZTitle("[ns]")
		time_rel2012[key].Draw("colz")
		c.SaveAs(outdir + "/" + time_rel2012[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	for key in timeError:
		timeError[key].SetAxisRange(0, .2, "Z")
		timeError[key].SetZTitle("[ns]")
		timeError[key].Draw("colz")
		c.SaveAs(outdir + "/" + timeError[key].GetName() + ".png")
		
	ROOT.gStyle.SetOptStat(1100)
	c = ROOT.TCanvas("c","c",1600,1200)
	for key in timeError1d:
		timeError1d[key].SetStats(True)
		timeError1d[key].Draw()
		print timeError1d[key].GetMean(), timeError1d[key].GetRMS()
		c.SaveAs(outdir + "/" + timeError1d[key].GetName() + ".png")

	ROOT.gStyle.SetOptStat(0)
	c = ROOT.TCanvas("c","c",1600,1200)
	for key in stdDev:
		stdDev[key].SetAxisRange(0, 3, "Z")
		stdDev[key].SetZTitle("[ns]")
		stdDev[key].Draw("colz")
		c.SaveAs(outdir + "/" + stdDev[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	c.SetLogz(True)
	if occupancy:
		occu_max = max( [ occupancy[key].GetMaximum() for key in occupancy])
	for key in occupancy:
		occupancy[key].SetAxisRange(0, occu_max, "Z")
		occupancy[key].SetZTitle("Events")
		occupancy[key].Draw("colz")
		c.SaveAs(outdir + "/" + occupancy[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	if energy:
		en_max = max( [ energy[key].GetMaximum() for key in energy])
	en_max = 5.0
	for key in energy:
		energy[key].Draw("colz")
		energy[key].SetAxisRange(0, en_max, "Z")
		energy[key].SetZTitle("[GeV]")
		c.SaveAs(outdir + "/" + energy[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	for key in iRing:
		graph = ROOT.TGraphErrors(iRing[key])
		graph.Draw("AP")
		iRing[key].Draw()
		c.SaveAs(outdir + "/" + iRing[key].GetName() + ".png")

	for key in iRingError:
		graph = ROOT.TGraphErrors(iRingError[key])
		graph.Draw("AP")
		iRingError[key].Draw()
		c.SaveAs(outdir + "/" + iRingError[key].GetName() + ".png")
	
	c = ROOT.TCanvas("c","c",1600,1200)
	for key in EvsT:
		EvsT[key].Draw("colz")
		c.SaveAs(outdir + "/" + EvsT[key].GetName() + ".png")

	c = ROOT.TCanvas("c","c",1600,1200)
	ROOT.gStyle.SetOptStat(1100)
	for key in time1d:
		time1d[key].SetStats(True)
		time1d[key].Draw()
		addFitToPlot(time1d[key],os.path.join(outdir, time1d[key].GetName() + ".png"))
	
	return time

if __name__ == "__main__":

	customROOTstyle()
	ROOT.gROOT.SetBatch(True)
	print sys.argv
	prefix = sys.argv[1]
	filename = sys.argv[2]

	if len(sys.argv) == 3:
		#if len(sys.argv) > 1:
		#	outdir = sys.argv[1]
		#elif filename.startswith("output"):
			# use same path as input file with output -> plots
		dir, basename = os.path.split(filename)
		dir = dir.split('/')
		print dir[-1:]
		outdir = '/'.join(dir[:-1]) + "/plots/" + dir[-1]
		outdir = os.path.normpath(outdir)
	elif len(sys.argv) == 4:
		outdir = sys.argv[3]

	def mkdir_p(path):
		try:
			os.makedirs(path)
		except OSError as exc: # Python >2.5
			if exc.errno == errno.EEXIST and os.path.isdir(path):
				pass
			else: raise

	mkdir_p(outdir)
	shutil.copy("plots/index.php", outdir)

	file = ROOT.TFile.Open(filename)
	tree = file.Get("timing/EcalSplashTiming/timingTree")
	time = plotMaps(tree, outdir, prefix = prefix)

