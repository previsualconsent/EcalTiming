import ROOT
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle

import sys

def float2name(x):
	return ("%.1f" % x).replace('.','_')

customROOTstyle()
ROOT.gROOT.SetBatch(True)
filename = sys.argv[1]
outdir = "plots"
if len(sys.argv) > 2:
	outdir = sys.argv[2]

file = ROOT.TFile.Open(filename)


tree = file.Get("TriggerResults/EcalSplashTiming_0/energyStabilityTree")
c = ROOT.TCanvas()

#print "Finding list of cuts"
#cuts = list(set([event.min_energy for event in tree]))
#cuts.sort()

cuts = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
cuts = [0.5, 1.0, 1.5, ]
print "Cuts are",cuts

print "Finding max occupancy/energy"
#max_num = max([event.num for event in tree])
#max_energy = max([event.energy for event in tree])
max_num = 38341
max_energy = 68.5
print max_num,max_energy

def getBins(detector):
	if detector == "EB":
		iz = 0
		bins = "(360,1,361,171,-85,86)"
	elif detector == "EEM":
		iz = -1
		bins = "(100,1,101,100,1,101)"
	elif detector == "EEP":
		iz = 1
		bins = "(100,1,101,100,1,101)"
	return bins,iz

def makeTimePlots(detector,cut,tree,canvas):
	cut_str = float2name(cut)
	old_cut_str = float2name(cuts[i-1])

	canvas.SetLogz(False)
	name = detector + "_time_" + cut_str
	old_name = detector + "_time_" + old_cut_str
	h = ROOT.gDirectory.FindObject(old_name)
	hold = None
	if h:
		hold = h.Clone(old_name)
	
	bins,iz = getBins(detector)

	tree.Draw("ix:iy>>" + name + bins,"(iz==%d && min_energy == %.1f)*time" %(iz,cut),"colz")
	h = ROOT.gDirectory.FindObject(name)
	#h.GetZaxis().SetRangeUser(-10,10)
	h.SetTitle(detector + " Timing with E > %.1f" % cut)
	c.SaveAs(outdir + "/" + name + ".png")

	if hold:
		hold.Add(h,-1)
		hold.Scale(-1)
		hold.SetTitle(detector + " Diff  (E > %.1f) - (E > %.1f) " % (cut,cuts[i-1]))
		hold.GetZaxis().UnZoom()
		hold.Draw("colz")
		c.SaveAs(outdir + "/" + name + "_rel" + ".png")
	
def makeNumPlots(detector,cut,max_num,tree,canvas):
	cut_str = float2name(cut)

	canvas.SetLogz(True)

	name = detector + "_occupancy"
	bins,iz = getBins(detector)

	tree.Draw("ix:iy>>" + name + bins,"(iz==%d && min_energy == %.1f)*num" %(iz,cut),"colz")
	h = ROOT.gDirectory.FindObject(name)
	h.GetZaxis().SetRangeUser(0,max_num)
	h.SetTitle(detector + " Occupancy with E > %.1f" % cut)
	c.SaveAs(outdir + "/" + name + "_" + cut_str + ".png")


c = ROOT.TCanvas()
for i,cut in enumerate(cuts):
	print "Doing cut", cut
	cut_str = float2name(cut)

	makeTimePlots("EB",cut,tree,c)
	makeTimePlots("EEM",cut,tree,c)
	makeTimePlots("EEP",cut,tree,c)

	c.SetLogz(True)
	tree.Draw("ix:iy>>EB_num(360,1,361,171,-85,86)","(iz==0 && min_energy == %.1f)*num" %cut,"colz")
	h = ROOT.gDirectory.FindObject("EB_num")
	h.GetZaxis().SetRangeUser(0,max_num)
	h.SetTitle("Occupancy with E > %.1f" % cut)
	c.SaveAs(outdir + "/EB_occupancy_" + cut_str + ".png")
	
	tree.Draw("ix:iy>>EEM_num(100,1,101,100,1,101)","(iz==-1 && min_energy == %.1f)*num" %cut,"colz")
	h = ROOT.gDirectory.FindObject("EEM_num")
	h.GetZaxis().SetRangeUser(0,max_num)
	h.SetTitle("Occupancy with E > %.1f" % cut)
	c.SaveAs(outdir + "/EEM_occupancy_" + cut_str + ".png")

	tree.Draw("ix:iy>>EEP_num(100,1,101,100,1,101)","(iz==-1 && min_energy == %.1f)*num" %cut,"colz")
	h = ROOT.gDirectory.FindObject("EEP_num")
	h.GetZaxis().SetRangeUser(0,max_num)
	h.SetTitle("Occupancy with E > %.1f" % cut)
	c.SaveAs(outdir + "/EEP_occupancy_" + cut_str + ".png")

	tree.Draw("ix:iy>>EB_energy(360,1,361,171,-85,86)","(iz==0 && min_energy == %.1f)*energy" %cut,"colz")
	h = ROOT.gDirectory.FindObject("EB_energy")
	h.GetZaxis().SetRangeUser(0,max_energy)
	h.SetTitle("Energy with E > %.1f" % cut)
	c.SaveAs(outdir + "/EB_energy_" + cut_str + ".png")
	
	tree.Draw("ix:iy>>EEM_energy(100,1,101,100,1,101)","(iz==-1 && min_energy == %.1f)*energy" %cut,"colz")
	h = ROOT.gDirectory.FindObject("EEM_energy")
	h.GetZaxis().SetRangeUser(0,max_energy)
	h.SetTitle("Energy with E > %.1f" % cut)
	c.SaveAs(outdir + "/EEM_energy_" + cut_str + ".png")

	tree.Draw("ix:iy>>EEP_energy(100,1,101,100,1,101)","(iz==-1 && min_energy == %.1f)*energy" %cut,"colz")
	h = ROOT.gDirectory.FindObject("EEP_energy")
	h.GetZaxis().SetRangeUser(0,max_energy)
	h.SetTitle("Energy with E > %.1f" % cut)
	c.SaveAs(outdir + "/EEP_energy_" + cut_str + ".png")

