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


def inittime1d(name, title, iz):
	if iz == 0:
		det = "EB_"
	elif iz == -1:
		det = "EEM_"
	elif iz == 1:
		det = "EEP_"
	else:
		#print "bad iz value", iz
		det = str(iz)
	h = ROOT.TH1F(det + name, title, 50, -10, 10)
	h.SetXTitle("Time [ns]")
	h.SetYTitle("Events")
	return h


def initiRing(name, title, iz):
	if iz == 0:
		h = ROOT.TProfile("EB_" + name, title, 171, -85, 86)
	elif iz == -1:
		h = ROOT.TProfile("EEM_" + name, title, 39, 0, 39)
	elif iz == 1:
		h = ROOT.TProfile("EEP_" + name, title, 39, 0, 39)
	else:
		print "bad iz value", iz
		return None
	h.SetXTitle("iRing")
	h.SetYTitle("Mean Time [ns]")
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

def initHists(prefix,hist_dict, init_func, key, name, title):
	if key in hist_dict:
		return
	iz = key
	hist_dict[key] = init_func(prefix + name, title, iz)

def addFitToPlot(h):
	fit = ROOT.TF1("gaus","gaus")
	h.Fit(fit, "Q")
	mu = fit.GetParameter(1)
	sigma = fit.GetParameter(2)
	label = ROOT.TPaveText(.5, .7, .9, .9, "NDC")
	label.AddText("#mu = %.3f" % mu)
	label.AddText("#sigma = %.3f" % sigma)
	label.Draw()
	return mu,sigma


def plotCCUs(tree, outdir, prefix=""):
	c = ROOT.TCanvas("c","c",1600,1200)
	# dictionaries to store histograms
	time = dict()
	time_offset = dict()
	time_offset_ccu = dict()
	time_abs = dict()

	CCU = dict()
	CCU1d = dict()
	CCU_maps = dict()
	CCU_maps_cut = dict()
	CCU_err_maps = dict()
	elec_map = dict()
	counter = 0

	print "Found", tree.GetEntries(), "entries"
	if tree.GetEntries() == 0: sys.exit(-1)
	
	offset = dict()
	for iz in detectors:
		tree.Draw("time>>temp%d(50,-5,5)" % iz,"iz == %d && num != 0" % iz)
		h = ROOT.gDirectory.FindObject("temp%d" % iz)
		offset[iz],__ = addFitToPlot(h)
		c.SaveAs(outdir + '/' + detectors[iz] + "_1d_noffset.png")

	print "Global offset"
	for iz in offset:
		print "%d\t%.3f"%(iz, offset[iz])

	timing = dict()
	from EcalTiming.EcalTiming.loadOldCalib import getCalib,getRawIDMap
	oldCalib = getCalib()
	rawidMap = getRawIDMap()

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
		initHists(prefix,time, initMap, key, "time", "Time Shifts [ns]")
		initHists(prefix,time_offset, initMap, key, "time_offset", "Time Shifts - Global [ns]")
		initHists(prefix,time_offset_ccu, initMap, key, "time_offset_ccu", "Time Shifts - Global - HW [ns]")
		initHists(prefix,time_abs, initMap, key, "time_abs", "Absolute Time [ns]")

		initHists(prefix,CCU, inittime1d, (event.elecID), "ccu_time", " CCU Time [ns]")
		initHists(prefix,CCU1d, inittime1d, key, "ccu_time1d", " CCU Time [ns]")
		initHists(prefix,CCU_maps, initMap, key, "time_ccu", "CCU Shifts Map [ns]")
		initHists(prefix,CCU_maps_cut, initMap, key, "time_ccu_cut", "CCU Shifts Map [ns]")
		initHists(prefix,CCU_err_maps, initMap, key, "timeError_ccu", "StdDev of Crystals in CCU [ns]")
		
		elec_map[( event.ix, event.iy, iz, event.rawid)] = event.elecID
		
		# fill histograms
		if iz == 0:
			x = event.iy
			y = event.ix
		else:
			x = event.ix
			y = event.iy

		
		time[key].Fill(x, y, event.time)
		time_offset[key].Fill(x, y, event.time - offset[iz])
		CCU[event.elecID].Fill(event.time - offset[iz])
		time_abs[iz].Fill(x,y, event.time - offset[iz] - oldCalib[event.rawid])

	ccu_adj = {(54, 19): 4.0, (54, 20): 4.0, (48,  1): 2.0, (48,  2): 1.0, (48,  7): 2.0, (48,  5): 2.0, (48,  6): 1.0, (48,  3): 1.0, (48,  8): 1.0, (48,  4): 2.0, ( 1, 19): 4.0}

	print "CCU shifts"
	unit = 25./24.
	for id,crys in rawidMap.iteritems():
		if(crys.FED,crys.CCU) in ccu_adj:
			if crys.iz == 0:
				x = crys.iy
				y = crys.ix
			else:
				x = crys.ix
				y = crys.iy
			CCU_maps_cut[crys.iz].Fill(x,y,ccu_adj[(crys.FED,crys.CCU)])

	r = 3
	for key in CCU_maps:
		CCU_maps[key].SetAxisRange(-r, r, "Z")
		CCU_maps[key].SetZTitle("[ns]")
		CCU_maps[key].Draw("colz")
		c.SaveAs(outdir + "/" + CCU_maps[key].GetName() + ".png")

	for key in CCU_maps_cut:
		CCU_maps_cut[key].SetAxisRange(-r, r, "Z")
		CCU_maps_cut[key].SetZTitle("[ns]")
		CCU_maps_cut[key].Draw("colz")
		c.SaveAs(outdir + "/" + CCU_maps_cut[key].GetName() + ".png")

	for key in CCU_err_maps:
		CCU_err_maps[key].SetAxisRange(0, 2, "Z")
		CCU_err_maps[key].SetZTitle("[ns]")
		CCU_err_maps[key].Draw("colz")
		c.SaveAs(outdir + "/" + CCU_err_maps[key].GetName() + ".png")
		
	for key in time:
		time[key].SetAxisRange(-r, r, "Z")
		time[key].SetZTitle("[ns]")
		time[key].Draw("colz")
		c.SaveAs(outdir + "/" + time[key].GetName() + ".png")

	for key in time_offset:
		time_offset[key].SetAxisRange(-r, r, "Z")
		time_offset[key].SetZTitle("[ns]")
		time_offset[key].Draw("colz")
		c.SaveAs(outdir + "/" + time_offset[key].GetName() + ".png")

	for key in time_offset_ccu:
		time_offset_ccu[key].Add(time_offset[key], CCU_maps_cut[key], 1, -1 )
		time_offset_ccu[key].SetAxisRange(-r, r, "Z")
		time_offset_ccu[key].SetZTitle("[ns]")
		time_offset_ccu[key].Draw("colz")
		c.SaveAs(outdir + "/" + time_offset_ccu[key].GetName() + ".png")

	def plotOutOfRange(h,hcut,low,high):
		ncells =  h.GetNcells()
		for i in range(ncells):
			val = h.GetBinContent(i)
			if val < low or val > high:
				hcut.SetBinContent(i,val)
				hcut.SetBinEntries(i,1)
			 	x,y,z = ROOT.Long(),ROOT.Long(),ROOT.Long()
			 	h.GetBinXYZ(i,x,y,z)
				print h.GetName(), x,y,z, val

	for key in time_abs:
		time_abs[key].Add(CCU_maps_cut[key], -1)
		time_abs[key].SetAxisRange(-10, 10, "Z")
		time_abs[key].SetZTitle("[ns]")
		time_abs[key].Draw("colz")
		c.SaveAs(outdir + "/" + time_abs[key].GetName() + ".png")
		
		time_abs_oot = initMap("time_abs_oot", "Absolute Time OOT [ns]",key)
		plotOutOfRange(time_abs[key], time_abs_oot, -10,10)
		time_abs_oot.SetZTitle("[ns]")
		time_abs_oot.Draw("colz")
		c.SaveAs(outdir + "/" + time_abs_oot.GetName() + ".png")


	for key in CCU1d:
		CCU1d[key].Draw()
		c.SaveAs(outdir + "/" + CCU1d[key].GetName() + ".png")

	return time

if __name__ == "__main__":

	customROOTstyle()
	ROOT.gROOT.SetBatch(True)
	filename = sys.argv[1]

	#if len(sys.argv) > 1:
	#	outdir = sys.argv[1]
	#elif filename.startswith("output"):
		# use same path as input file with output -> plots
	dir, basename = os.path.split(filename)
	dir = dir.split('/')
	print dir[-1:]
	outdir = '/'.join(dir[:-1]) + "/plots/" + dir[-1]
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

	file = ROOT.TFile.Open(filename)
	tree = file.Get("filter/EcalSplashTiming/timingTree")
	time = plotCCUs(tree, outdir, )


