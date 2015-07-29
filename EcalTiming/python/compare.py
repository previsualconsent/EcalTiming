import ROOT
from EcalTiming.EcalTiming.loadOldCalib import getCalib,getCalibFromFile, getRawIDMap
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle

customROOTstyle()

oldCalib = getCalib()
rawidMap = getRawIDMap()
simone = getCalibFromFile("PhiSimmetry_run251252.dat")
peter = getCalibFromFile("/afs/cern.ch/work/p/phansen/public/EcalTiming/round1/AlCaPhiSym-251252/ecalTimeRelative-251252-0_numEvent5000000-corr.dat")

outdir = "plots/simone252/" 

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
	h = ROOT.TH1F(det + name, title, 50, -10,30)
	h.SetXTitle("Time [ns]")
	h.SetYTitle("Events")
	return h

hpeter = dict()
hsimone = dict()
hpeter1d = dict()
hsimone1d = dict()
holdCalib = dict()
hdiff = dict()
hdiff1d = dict()
for iz in [-1,0,1]:
	hpeter[iz] = initMap("peter","peter",iz)
	hsimone[iz] = initMap("simone","simone",iz)
	holdCalib[iz] = initMap("oldCalib","oldCalib",iz)
	hdiff[iz] = initMap("diff","diff",iz)
	hpeter1d[iz] = inittime1d("peter1d", "peter1d",iz)
	hsimone1d[iz] = inittime1d("simone1d", "simone1d",iz)
	hdiff1d[iz] = inittime1d("diff1d", "diff1d",iz)


#means = {0:0.398 + 0.5, -1:-1.130, 1:-0.832}
#means = {0:0.398 + 0.5, -1:-1.130, 1:-0.832}
#simone_means = {0:.5,  -1:12, 1:12}
means = {0:0, -1:0, 1:0}
simone_means = {0:0,  -1:0, 1:0}
ids = set(simone) & set(peter) & set(rawidMap)
print len(ids)
for id in ids:
	crystal= rawidMap[id]
	iz = crystal.iz
	if iz == 0:
		x = crystal.iy
		y = crystal.ix
	else:
		x = crystal.ix
		y = crystal.iy
	

	hsimone[iz].Fill(x,y,simone[id] - simone_means[iz])
	hpeter[iz].Fill(x,y,peter[id] + means[iz])
	holdCalib[iz].Fill(x,y,oldCalib[id])
	hdiff[iz].Fill(x,y,simone[id] - simone_means[iz] - (oldCalib[id] - peter[id] - means[iz]))
	hpeter1d[iz].Fill(peter[id] + means[iz])
	hsimone1d[iz].Fill(simone[id]-simone_means[iz])
	hdiff1d[iz].Fill(simone[id]-simone_means[iz] - (oldCalib[id] - peter[id] - means[iz]))


c = ROOT.TCanvas("c","c")
for h in hsimone.values() + holdCalib.values():
	h.SetAxisRange(-10,10,"Z")
	h.Draw("colz")
	c.SaveAs(outdir + h.GetName() + ".png")

for h in hpeter.values():
	h.SetAxisRange(-10,10,"Z")
	h.Draw("colz")
	c.SaveAs(outdir + h.GetName() + ".png")

for iz in hdiff:
	h = hdiff[iz]
	h.SetAxisRange(-10,10,"Z")
	h.Draw("colz")
	c.SaveAs(outdir + h.GetName() + ".png")

for h in hdiff1d.values() + hpeter1d.values() + hsimone1d.values():
	h.Draw()
	c.SaveAs(outdir + h.GetName() + ".png")

#if __name__ == "__main__":
#	customROOTstyle()
#	ROOT.gROOT.SetBatch(True)
#	filename = sys.argv[1]
#
#	#if len(sys.argv) > 1:
#	#	outdir = sys.argv[1]
#	#elif filename.startswith("output"):
#		# use same path as input file with output -> plots
#	dir, basename = os.path.split(filename)
#	dir = dir.split('/')
#	print dir[-1:]
#	outdir = '/'.join(dir[:-1]) + "/plots/" + dir[-1]
#	outdir = os.path.normpath(outdir)
#
#	def mkdir_p(path):
#		try:
#			os.makedirs(path)
#		except OSError as exc: # Python >2.5
#			if exc.errno == errno.EEXIST and os.path.isdir(path):
#				pass
#			else: raise
#
#	mkdir_p(outdir)
#	shutil.copy("plots/index.php", outdir)
