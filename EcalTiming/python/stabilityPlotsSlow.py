import ROOT
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle,customPalette

import os,sys,errno,shutil

customROOTstyle()
ROOT.gROOT.SetBatch(True)
filename = sys.argv[1]

detectors = {-1:"EEM", 0:"EB", 1:"EEP"}

dir, basename = os.path.split(filename)
dir = dir.split('/')
print dir[-1:]
outdir = '/'.join(dir[:-1]) + "/plots/" + dir[-1]
outdir = os.path.normpath(outdir)

from EcalTiming.EcalTiming.loadOldCalib import getCalib
oldCalib = getCalib()

outdir = os.path.join(outdir, 'stability')
outdir_backup = os.path.join(outdir, 'backup')

def mkdir_p(path):
   try:
      os.makedirs(path)
   except OSError as exc: # Python >2.5
      if exc.errno == errno.EEXIST and os.path.isdir(path):
         pass
      else: raise

mkdir_p(outdir)
mkdir_p(outdir_backup)
shutil.copy("plots/index.php",outdir)
shutil.copy("plots/index.php",outdir_backup)



file = ROOT.TFile.Open(filename)

def float2name(x):
	return ("%.1f" % x).replace('.','_')

def initMap(name,title,iz):
	if iz == 0:
		return ROOT.TProfile2D("EB_" + name,title,360,1,361,171,-85,86)
	elif iz == -1:
		return ROOT.TProfile2D("EEM_" + name,title,100,1,101,100,1,101)
	elif iz == 1:
		return ROOT.TProfile2D("EEP_" + name,title,100,1,101,100,1,101)
	else:
		print "bad iz value",iz
		return None

def inittime1d(name,title,iz):
	if iz == 0:
		det = "EB_"
	elif iz == -1:
		det = "EEM_"
	elif iz == 1:
		det = "EEP_"
	else:
		print "bad iz value",iz
		return None
	return ROOT.TH1F(det + name,title,50,-10,10)

def initiRing(name,title,iz):
	if iz == 0:
		return ROOT.TProfile("EB_" + name,title,171,-85,86)
	elif iz == -1:
		return ROOT.TProfile("EEM_" + name,title,39,0,39)
	elif iz == 1:
		return ROOT.TProfile("EEP_" + name,title,39,0,39)
	else:
		print "bad iz value",iz
		return None
	
def initHists(hist_dict,init_func,key, name, title):
	if key in hist_dict:
		return
	cut,iz = key
	hist_dict[key] = init_func(name,title,iz)

tree = file.Get("filter/EcalSplashTiming/energyStabilityTree")
c = ROOT.TCanvas("c","c",1600,900)
# dictionaries to store histograms
time = dict()
occupancy = dict()
energy = dict()
iRing = dict()
time1d = dict()
counter = 0

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

offset = dict()
for iz in detectors:
	tree.Draw("time>>temp%d(50,-5,5)" % iz,"iz == %d && num != 0" % iz)
	h = ROOT.gDirectory.FindObject("temp%d" % iz)
	offset[iz],__ = addFitToPlot(h)
	c.SaveAs(outdir + '/' + detectors[iz] + "_1d_nooffset.png")

print "Found",tree.GetEntries(),"entries"
if tree.GetEntries() == 0: sys.exit(-1)
for event in tree:
	if not counter % (tree.GetEntries()/10): print counter, '/', tree.GetEntries()
	counter += 1
	if event.num == 0: continue
	# make dictionary key
	index = ord(event.index)
	cut_str = str(index)
	iz = ord(event.iz)
	if iz == 255: iz = -1
	key = (index,iz)
	# initialize histograms (if they haven't been made yet
	initHists(time, initMap, key, "time_" + cut_str, "Timing: step" + cut_str)
	initHists(occupancy, initMap, key, "occupancy_" + cut_str, "Occupancy: step" + cut_str)
	initHists(energy, initMap, key, "energy_" + cut_str, "Energy: step" + cut_str)

	initHists(iRing, initiRing, key, "iRing_" + cut_str, "iRing: step" + cut_str)
	initHists(time1d, inittime1d, key, "time1d_" + cut_str, "time1d: step" + cut_str)
	
	# fill histograms
	if iz == 0:
		x = event.iy
		y = event.ix
	else:
		x = event.ix
		y = event.iy

	t = event.time - offset[iz]

	time[key].Fill(x, y, t)
	occupancy[key].Fill(x, y, event.num)
	energy[key].Fill(x, y, event.energy)

	iRing[key].Fill(float(event.iRing), t)
	time1d[key].Fill(t)
	#if event.rawid in oldCalib:
	#	t += oldCalib[event.rawid]
	#else:
	#	print "Rawid not found", event.rawid 

for key in time:
	time[key].SetZTitle("[ns]")
	time[key].SetAxisRange(-10,10,"Z")
	time[key].Draw("colz")
	c.SaveAs(outdir_backup + "/" + time[key].GetName() + ".10.png")
	time[key].SetAxisRange(-5,5,"Z")
	time[key].Draw("colz")
	c.SaveAs(outdir_backup + "/" + time[key].GetName() + ".5.png")
	time[key].SetAxisRange(-2,2,"Z")
	time[key].Draw("colz")
	c.SaveAs(outdir_backup + "/" + time[key].GetName() + ".2.png")

c.SetLogz(True)
occu_max = max( [ occupancy[key].GetMaximum() for key in occupancy])
for key in occupancy:
	occupancy[key].SetAxisRange(0,occu_max,"Z")
	occupancy[key].SetZTitle("Events")
	occupancy[key].Draw("colz")
	c.SaveAs(outdir_backup + "/" + occupancy[key].GetName() + ".png")

c.SetLogz(False)
en_max = max( [ energy[key].GetMaximum() for key in energy])
en_max = 5.0
for key in energy:
	energy[key].Draw("colz")
	energy[key].SetAxisRange(0,en_max,"Z")
	energy[key].SetZTitle("[GeV]")
	c.SaveAs(outdir_backup + "/" + energy[key].GetName() + ".png")

colors = [ROOT.kBlack,ROOT.kRed,ROOT.kGreen,ROOT.kBlue,ROOT.kMagenta,ROOT.kGray]
markers = [ROOT.kFullCircle, ROOT.kFullSquare]

ROOT.gStyle.SetHistLineWidth(1);
for iz in [-1,0,1]:
	keys = sorted([ (cut,iz) for cut,i in time if i == iz])
	if not keys: continue
	ic = 0
	leg = ROOT.TLegend(0.15 ,0.15, 0.48, 0.35)
	leg.SetNColumns(3)
	leg.SetHeader("Mean time in iRing")
	mg = ROOT.TMultiGraph()
	for i in range(1,len(keys)):
		iRing_rel = initiRing("iRing_rel_%d_%d" % (i, i-1), "iRing Diff Step%d - Step%d" % (i, i-1), keys[i][1])
		iRing_rel.Add(iRing[keys[i]],iRing[keys[i-1]], 1, -1)

		graph = ROOT.TGraphErrors(iRing_rel)
		graph.SetLineColor(colors[ic % len(colors)])
		graph.SetMarkerColor(colors[ic % len(colors)])
		graph.SetMarkerSize(1)
		graph.SetMarkerStyle(markers[(ic / len(colors)) % len(markers)])
		leg.AddEntry(graph,"Step %d - %d" % (i,i-1), "ple")
		ic+=1
		mg.Add(graph)

	mg.Draw("ALP")
	leg.Draw()
	c.SaveAs(outdir + "/" + iRing[keys[0]].GetName() + ".png")

for key in time1d:
	time1d[key].Draw()
	c.SaveAs(os.path.join(outdir, time1d[key].GetName() + ".png"))

for iz in [-1,0,1]:
	keys = sorted([ (cut,iz) for cut,i in time if i == iz])
	if not keys: continue
	for i in range(1,len(keys)):
		c.SetLogz(False)
		customPalette()
		hrel = initMap("time_rel_%d_%d" % (i, i-1), "Time Diff Step%d - Step%d" % (i, i-1), keys[i][1])
		h1 = time[keys[i]]
		h0 = time[keys[i-1]]
		hrel.Add(h1,h0,1,-1)
		hrel.SetAxisRange(-.2,.2,"Z")
		hrel.Draw("colz")
		c.SaveAs(outdir + "/" + hrel.GetName() + ".png")
		
		if i != 1:
			hrel0 = initMap("time_rel_%d_%d" % (i, 0), "Time Diff Step%d - Step%d" % (i, 0), keys[i][1])
			hrel0.SetAxisRange(-.2,.2,"Z")
			hrel0.Add(time[keys[i]],time[keys[0]],1,-1)
			hrel0.Draw("colz")
			c.SaveAs(outdir + "/" + hrel0.GetName() + ".png")

		c.SetLogz(True)
		ROOT.gStyle.SetPalette(55)
		hnum = occupancy[keys[i]]
		hnumold = occupancy[keys[i-1]]
		hnumold.Add(hnum,-1)
		hnumold.SetTitle(detectors[iz] + " Num Diff Step%d - Step%d" % (keys[i][0],keys[i-1][0]))
		hnumold.SetAxisRange(0,hnumold.GetBinContent(hnumold.GetMaximumBin()),"Z")
		hnumold.Draw("colz")
		c.SaveAs(outdir_backup + "/" + hnum.GetName() + "_" + str(keys[i-1][0]) + "_rel.png")
