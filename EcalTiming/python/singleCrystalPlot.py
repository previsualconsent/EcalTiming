import ROOT
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle, customPalette
import math

import os
import sys
import errno
import shutil

flag_dict = {
		"high_skew"  :"0x01",
		"unstable_en":"0x02",
		"ccu_oot"    :"0x04",
		"ring"       :"0x08",
		"crys"       :"0x10",
		}

flag_dict_int = {
		"high_skew"  :0x01,
		"unstable_en":0x02,
		"ccu_oot"    :0x04,
		"ring"       :0x08,
		"crys"       :0x10,
		}

def getStatus(flag):
	flag_value = flag_dict[flag]
	return "( (status & " + flag_value + ") == " + flag_value + ")"

def char2int(x, signed = False):
	if type(x) == type("s"):
		xout = ord(x)
		if signed and xout >= 255:
			xout -= 256
	else:
		xout = x
	return xout

def makeCrystalHists(flag,id):
	name = flag + "_" + str(id) + "_"
	title = flag + " " + str(id) + " "
	return [ ROOT.TH1F(name + "time", title + "Time", 200,-20,20),
	  		ROOT.TH2F(name + "en_time", title + "Energy vs Time", 40, 0, 20, 200,-20,20),
	  		ROOT.TProfile(name + "en_time_prof", title + "Time Profile", 40, 0, 20),
	  		]
def fillCrystalHists(hists,event):
	hists[0].Fill(event.time)
	hists[1].Fill(event.energy, event.time)
	hists[2].Fill(event.energy, event.time)

def singleCrystalDump(tree, outdir):
	flags = ['high_skew', 'unstable_en','crys']

	hists = dict()
	print "Start of Tree Loop"
	for event in tree:
		iz = char2int(event.iz, signed=True)
		status = char2int(event.status)
		for flag in flags:
			if status & flag_dict_int[flag]:
				key = (flag, event.rawid)
				if key not in hists:
					hists[key] = makeCrystalHists(*key)
				fillCrystalHists(hists[key], event)
	
	c = ROOT.TCanvas("c","c",1600,1200)
	for h in hists.values():
		ROOT.gStyle.SetOptStat(220112210)
		h[0].Draw()
		c.SaveAs(outdir + "/" + h[0].GetName() + ".png")
		ROOT.gStyle.SetOptStat(1110000)
		h[1].Draw("colz")
		h[2].Draw("same")
		c.SaveAs(outdir + "/" + h[1].GetName() + ".png")

	print "End of Tree Loop"
	

if __name__ == "__main__":

	customROOTstyle()
	ROOT.gROOT.SetBatch(True)
	ROOT.gStyle.SetOptStat(1)
	print sys.argv
	filename = sys.argv[1]
	prefix = sys.argv[2]

	dir, basename = os.path.split(filename)
	dir = dir.split('/')
	print dir[-1:]
	outdir = '/'.join(dir[:-1]) + "/plots/single-crystal/" + dir[-1]
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
	tree = file.Get("filter/EcalSplashTiming/dumpTree")
	singleCrystalDump(tree, outdir)

