#include "EcalTiming/EcalTiming/interface/EcalCrystalTimingCalibration.h"
#include <cassert>

float EcalCrystalTimingCalibration::getNumWithinNSigma(float n_sigma, float maxRange) const
{

	if(_numWithinNSigma.count(n_sigma) == 0) calcAllWithinNSigma(n_sigma, maxRange);
	return _numWithinNSigma[n_sigma];
}

float EcalCrystalTimingCalibration::getMeanWithinNSigma(float n_sigma, float maxRange) const
{

	if(_numWithinNSigma.count(n_sigma) == 0) calcAllWithinNSigma(n_sigma, maxRange);
	return _sumWithinNSigma[n_sigma] / _numWithinNSigma[n_sigma];
}

float EcalCrystalTimingCalibration::getStdDevWithinNSigma(float n_sigma, float maxRange) const
{

	float mean = getMeanWithinNSigma(n_sigma, maxRange); //variables are calculated by that
	return sqrt(_sum2WithinNSigma[n_sigma] / _numWithinNSigma[n_sigma] - mean * mean);
}

float EcalCrystalTimingCalibration::getMeanErrorWithinNSigma(float n_sigma, float maxRange) const
{

	float stddev = getStdDevWithinNSigma(n_sigma, maxRange); //variables are calculated by that
	return stddev / sqrt(_numWithinNSigma[n_sigma]);
}

float EcalCrystalTimingCalibration::getSkewnessWithinNSigma(float n_sigma, float maxRange) const
{

	float mean = getMeanWithinNSigma(n_sigma, maxRange); //variables are calculated by that
	float stdDev = getStdDevWithinNSigma(n_sigma, maxRange);
	return (_sum3WithinNSigma[n_sigma] / _numWithinNSigma[n_sigma] - 3 * mean * stdDev * stdDev - mean * mean * mean) / (stdDev * stdDev * stdDev);

}


// store the results such that you do only one loop over the events
void EcalCrystalTimingCalibration::calcAllWithinNSigma(float n_sigma, float maxRange) const
{
	//std::cout << timingEvents.size() << ' ' << _storingEvents;
	//std::cout << *this << std::endl;
	//assert(timingEvents.size() != 0 || !_storingEvents);
	assert(timingEvents.size() == num() || !_storingEvents);

	float range = std::min(maxRange, stdDev() * n_sigma);

	_sumWithinNSigma[n_sigma] = 0.;
	_sum2WithinNSigma[n_sigma] = 0;
	_sum3WithinNSigma[n_sigma] = 0.;
	_numWithinNSigma[n_sigma] = 0.;

	if(!_storingEvents) 
	{
		_sumWithinNSigma[n_sigma] = _sum;
		_sum2WithinNSigma[n_sigma] = _sum2;
		_sum3WithinNSigma[n_sigma] = 0;
		_numWithinNSigma[n_sigma] = _num;
	}

	for(auto te : timingEvents) {
		if(fabs(te.time() - mean()) < range) {
			_sumWithinNSigma[n_sigma] += te.time();
			_sum2WithinNSigma[n_sigma] += te.time() * te.time();
			_sum3WithinNSigma[n_sigma] += te.time() * te.time() * te.time();
			_numWithinNSigma[n_sigma]++;
		}
	}
	return;
}

bool EcalCrystalTimingCalibration::isStableInEnergy(float min, float max, float step, std::vector<std::pair<float,EcalCrystalTimingCalibration*> > &cutLevels)
{
	if(timingEvents.size() == 0) return true;
	unsigned int nSteps = std::round((max - min) / step);

	assert(nSteps < 100);
	assert(nSteps > 1);

	cutLevels.clear();
	float energy = min;
	for(unsigned int index = 0; index < nSteps; ++index, energy += step) 
		cutLevels.push_back(std::pair<float,EcalCrystalTimingCalibration*>(energy, new EcalCrystalTimingCalibration()));

	for(auto te : timingEvents) {
		for(auto it : cutLevels)
		{
			if(te.energy() > it.first) {
				it.second->add(te, false);
			}
			else break;
		}
	}

	for( auto it : cutLevels) {
		float mean_ = it.second->mean();
		float meanError_ = it.second->meanError();
		
		float orig_mean = mean();
		float orig_meanError = meanError();

		if(it.second->num() < 30 ) break; // low statistics so move on.
		if( meanError_ > 1.41 * orig_meanError) break; // does not make any sense to continue if the error is too high

		if(abs(orig_mean - mean_) > orig_meanError ) return false; /// \todo define a better criterium
		// now requires only that the mean with higher energy threshold is within the calibration statistical uncertainty
	}
	return true;

}

void EcalCrystalTimingCalibration::dumpCalibToTree(TTree *tree, int rawid_, int ix_, int iy_, int iz_, unsigned int elecID_, int iRing_) const
{
	Float_t time;
  	Float_t timeError;
	UInt_t  n;
	if(_storingEvents)
	{
		time = getMeanWithinNSigma(2,10);
  		timeError = getMeanErrorWithinNSigma(2,10);
		n = getNumWithinNSigma(2,10);
	}
	else
	{
		time = mean();
  		timeError = meanError();
		n = num();
	}

	Float_t energy(meanE());
	UInt_t  rawid(rawid_);
	Short_t  ix(ix_);
 	UShort_t iy(iy_); 
	Char_t   iz(iz_);
	UShort_t elecID(elecID_);
	Short_t iRing(iRing_);

	if(tree->GetBranch("rawid") == NULL) tree->Branch("rawid", &rawid, "rawid/i");
	else tree->SetBranchAddress("rawid", &rawid);

	if(tree->GetBranch("ix") == NULL) tree->Branch("ix", &ix, "ix/S");
	else tree->SetBranchAddress("ix", &ix);

	if(tree->GetBranch("iy") == NULL) tree->Branch("iy", &iy, "iy/s");
	else tree->SetBranchAddress("iy", &iy);

	if(tree->GetBranch("iz") == NULL) tree->Branch("iz", &iz, "iz/B");
	else tree->SetBranchAddress("iz", &iz);

	if(tree->GetBranch("time") == NULL) tree->Branch("time", &time, "time/F");
	else tree->SetBranchAddress("time", &time);

	if(tree->GetBranch("timeError") == NULL) tree->Branch("timeError", &timeError, "timeError/F");
	tree->SetBranchAddress("timeError", &timeError);

	if(tree->GetBranch("energy") == NULL) tree->Branch("energy", &energy, "energy/F");
	tree->SetBranchAddress("energy", &energy);

	if(tree->GetBranch("num") == NULL) tree->Branch("num", &n, "num/i");
	else tree->SetBranchAddress("num", &n);

	if(tree->GetBranch("elecID") == NULL) tree->Branch("elecID", &elecID, "elecID/s");
	else tree->SetBranchAddress("elecID", &elecID);

	if(tree->GetBranch("iRing") == NULL) tree->Branch("iRing", &iRing, "iRing/S");
	else tree->SetBranchAddress("iRing", &iRing);

	tree->Fill();
}

void EcalCrystalTimingCalibration::dumpToTree(TTree *tree, int ix_, int iy_, int iz_, unsigned int status_, unsigned int elecID_, int iRing_)
{
	//assert(tree->GetEntries() == 0);
	Float_t time, timeError, energy;
	UInt_t rawid;

	Short_t  ix(ix_);
 	UShort_t iy(iy_); 
	Char_t   iz(iz_);
	UShort_t elecID(elecID_);
	UChar_t  status(status_);
	Short_t iRing(iRing_);

	if(tree->GetBranch("rawid") == NULL) tree->Branch("rawid", &rawid, "rawid/i");
	else tree->SetBranchAddress("rawid", &rawid);

	if(tree->GetBranch("ix") == NULL) tree->Branch("ix", &ix, "ix/S");
	else tree->SetBranchAddress("ix", &ix);

	if(tree->GetBranch("iy") == NULL) tree->Branch("iy", &iy, "iy/s");
	else tree->SetBranchAddress("iy", &iy);

	if(tree->GetBranch("iz") == NULL) tree->Branch("iz", &iz, "iz/B");
	else tree->SetBranchAddress("iz", &iz);

	if(tree->GetBranch("time") == NULL) tree->Branch("time", &time, "time/F");
	else tree->SetBranchAddress("time", &time);

	if(tree->GetBranch("timeError") == NULL) tree->Branch("timeError", &timeError, "timeError/F");
	tree->SetBranchAddress("timeError", &timeError);

	if(tree->GetBranch("energy") == NULL) tree->Branch("energy", &energy, "energy/F");
	tree->SetBranchAddress("energy", &energy);

	if(tree->GetBranch("status") == NULL) tree->Branch("status", &status, "status/b");
	else tree->SetBranchAddress("status", &status);

	if(tree->GetBranch("elecID") == NULL) tree->Branch("elecID", &elecID, "elecID/s");
	else tree->SetBranchAddress("elecID", &elecID);

	if(tree->GetBranch("iRing") == NULL) tree->Branch("iRing", &iRing, "iRing/S");
	else tree->SetBranchAddress("iRing", &iRing);

	for(auto te : timingEvents) {
		rawid = te.detid().rawId();
		time = te.time();
		energy = te.energy();
		timeError = te.timeError();
		tree->Fill();
	}
}


