import ROOT
from EcalTiming.EcalTiming.loadOldCalib import getCalib,getCalibFromFile, getRawIDMap
from EcalTiming.EcalTiming.PlotUtils import customROOTstyle

customROOTstyle()

oldCalib = getCalib()
rawidMap = getRawIDMap("/afs/cern.ch/user/p/phansen/public/ecal-timing/dump_EcalTimeCalibConstants_v07_offline__since_00204623_till_4294967295.dat")
simone = getCalibFromFile("Pi0_corr_run251643_thr_1_5GeV.dat")
peter = getCalibFromFile("/afs/cern.ch/work/p/phansen/public/EcalTiming/round1/AlCaPhiSym-251252/ecalTimeRelative-251252-0_numEvent5000000-corr.dat")

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
	h = ROOT.TH1F(det + name, title, 50, -2, 2)
	h.SetXTitle("Time [ns]")
	h.SetYTitle("Events")
	return h

hpeter = dict()
hsimone = dict()
holdCalib = dict()
hdiff = dict()
hdiff1d = dict()
for iz in [-1,0,1]:
	hpeter[iz] = initMap("peter","peter",iz)
	hsimone[iz] = initMap("simone","simone",iz)
	holdCalib[iz] = initMap("oldCalib","oldCalib",iz)
	hdiff[iz] = initMap("diff","diff",iz)
	hdiff1d[iz] = inittime1d("diff1d", "diff1d",iz)


means = {0:0.398 + 0.5, -1:-1.130, 1:-0.832}
ids = set(simone) & set(peter) & set(rawidMap)
print len(ids)
for id in ids:
	ix,iy,iz = rawidMap[id]
	if iz == 0:
		x = iy
		y = ix
	else:
		x = ix
		y = iy
	

	hsimone[iz].Fill(x,y,simone[id])
	hpeter[iz].Fill(x,y,peter[id])
	holdCalib[iz].Fill(x,y,oldCalib[id])
	hdiff[iz].Fill(x,y,simone[id] + (oldCalib[id] - peter[id] - means[iz]))
	hdiff1d[iz].Fill(simone[id] + (oldCalib[id] - peter[id] - means[iz]))


c = ROOT.TCanvas("c","c")
for h in hsimone.values() + holdCalib.values():
	h.SetAxisRange(-3,3,"Z")
	h.Draw("colz")
	c.SaveAs("plots/simone252/" + h.GetName() + ".png")

for h in hpeter.values():
	h.SetAxisRange(-2,2,"Z")
	h.Draw("colz")
	c.SaveAs("plots/simone252/" + h.GetName() + ".png")

for iz in hdiff:
	h = hdiff[iz]
	h.SetAxisRange(-1,1,"Z")
	h.Draw("colz")
	c.SaveAs("plots/simone252/" + h.GetName() + ".png")

for iz in hdiff1d:
	hdiff1d[iz].Draw()
	c.SaveAs("plots/simone252/" + hdiff1d[iz].GetName() + ".png")

