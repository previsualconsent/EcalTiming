#ifndef ecaltimingcalibproducer_h
#define ecaltimingcalibproducer_h
/** \class EcalTimingCalibProducer EcalTimingCalibProducer.h EcalTiming/EcalTiming/plugins/EcalTimingCalibProducer.h
    \brief Plugin that derives the calibration constants

 This plugin runs over the events, selects the recHits according to the criteria defined in addRecHit

 \todo Exit condition based on convergence

*/

/**
   Module description:
 - digi to calibrated recHit reconstruction
 - selection of events with reasonable activity: minimum number of recHits
 - select recHits based on:
   - recoFlag -> only good recHits (exclude OOT pileup contribution with MultiFit)
   - minimum energy, ring based threshold
 - save all the time events (recHits) passing the selection
 - discard those not within 2 sigma of the stdDev distribution for the single channel (then excluding OOT spurious events)
 - exclude events with large time error (> 3ns) or null time error (==0 ns)
 - verify that the distribution is symmetric
 - check stability vs energy of the single channel within uncertainty
 - save full dump of time events in TTree for further checks if:
   - distribution not symmetric
   - time calibration not stable vs energy
 - calculate global time for EB, EE


 */
//#define DEBUG
#define RAWIDCRY 838904321

/// The entire set of events are saved for one channel in EB and one channel in EE in order to debug
#define EBCRYex 838861346
#define EECRYex 872422180

/// For one ring in EB, one in EE+ and one in EE- the entire set of events are saved to debug
#define EBRING 1
#define EEmRING 20
#define EEpRING 20

#define SPEEDOFLIGHT 30.0 // (cm/ns)
#define HW_UNIT 1.1 //(ns)

// system include files
#include <memory>
#include <iostream>
#include <fstream>

// Make Histograms the way!!
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDConsumerBase.h"

#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
//#include "FWCore/Framework/interface/Handle.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/Handle.h"
//#include "FWCore/Framework/interface/LooperFactory.h"
//#include "FWCore/Framework/interface/ESProducerLooper.h"
#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/ESProducts.h"
#include "FWCore/Framework/interface/Event.h"
// input collections
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
//RingTools
#include "Calibration/Tools/interface/EcalRingCalibrationTools.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloGeometry/interface/CaloSubdetectorGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/EcalMapping/interface/EcalElectronicsMapping.h"
#include "Geometry/EcalMapping/interface/EcalMappingRcd.h"

// record to be produced:
#include "CondFormats/DataRecord/interface/EcalTimeCalibConstantsRcd.h"
#include "CondFormats/DataRecord/interface/EcalTimeCalibErrorsRcd.h"
#include "CondFormats/DataRecord/interface/EcalTimeOffsetConstantRcd.h"
#include "CondTools/Ecal/interface/EcalTimeCalibConstantsXMLTranslator.h"
#include "CondTools/Ecal/interface/EcalTimeCalibErrorsXMLTranslator.h"
#include "CondTools/Ecal/interface/EcalTimeOffsetXMLTranslator.h"
#include "CondTools/Ecal/interface/EcalCondHeader.h"

#include "CondFormats/EcalObjects/interface/EcalTimeCalibConstants.h"
#include "CondFormats/EcalObjects/interface/EcalTimeCalibErrors.h"
#include "CondFormats/EcalObjects/interface/EcalTimeOffsetConstant.h"

#include "EcalTiming/EcalTiming/interface/EcalTimingEvent.h"
#include "EcalTiming/EcalTiming/interface/EcalCrystalTimingCalibration.h"

#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"

#include "TProfile.h"
#include "TGraphErrors.h"
#include "TGraph.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TFile.h"
#include "TProfile2D.h"

#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <map>
#include <vector>
#include <algorithm>
#include <functional>
#include <set>
#include <assert.h>
#include <time.h>

#include <TMath.h>
#include <Math/VectorUtil.h>
//#include <boost/tokenizer.hpp>

#include "EcalTiming/EcalTiming/interface/EcalTimeCalibrationMapFwd.h"

class EcalTimingCalibProducer : public edm::EDFilter
{

private:
	EcalTimeCalibrationMap _timeCalibMap; ///< calibration map: contains the time shift for each crystal
	EventTimeMap _eventTimeMap;           ///< container of recHits passing selection in the event (reset at each event)
	EcalHWCalibrationMap _HWCalibrationMap; //!<  The keys for this map are EcalElectronicIds with xtalid = stripid = 1
	///< calibration map for the CCU's (Hardware Constants).

	// For finding averages for specific eta ring
	EcalCrystalTimingCalibration timeEEP; ///< global time calibration of EE+
	EcalCrystalTimingCalibration timeEEM; ///< global time calibration of EE-
	EcalCrystalTimingCalibration timeEB; ///< global time calibration of EB
	EcalCrystalTimingCalibration timeEBRing; ///< global time calibration of one EB ring
	EcalCrystalTimingCalibration timeEEmRing; ///< global time calibration of one EE- ring
	EcalCrystalTimingCalibration timeEEpRing; ///< global time calibration of one EE+ ring
	EcalCrystalTimingCalibration timeEBCRYex; ///< global time calibration of one EB channel
	EcalCrystalTimingCalibration timeEECRYex; ///< global time calibration of one EE channel

public:
	EcalTimingCalibProducer(const edm::ParameterSet&); // default constructor
	~EcalTimingCalibProducer();                        // default destructor


	virtual void beginJob() override;
	virtual bool filter(edm::Event&, const edm::EventSetup&) override;
	virtual void endJob() override;


private:
	// ----------member data ---------------------------
	/** @name Input Parameters
	 * Parameters defined in the config file _cfi,py
	 */
	///@{

	unsigned int _maxLoop; ///< maximum number of loops for intercalibration
	bool _isSplash; ///< flag to activate for splash analysis
	bool _makeEventPlots; ///< flag for making plots for each event (meant for splashes)
	edm::InputTag _ecalRecHitsEBTAG; ///< input collection
	edm::InputTag _ecalRecHitsEETAG;///< input collection
	std::vector<int> _recHitFlags; ///< vector containing list of valid rec hit flags for calibration
	unsigned int _recHitMin; ///< require at least this many rec hits to count the event
	double _minRecHitEnergyStep; ///< to check step size to check energy stability
	double _minRecHitEnergyNStep; ///< number of steps to check energy stability
	double _energyThresholdOffsetEB; ///< energy to add to the minimum energy thresholc
	double _energyThresholdOffsetEE; ///< energy to add to the minimum energy thresholc
	double _chi2ThresholdOffsetEB; //chi2 square thr for the Barrel --- Added
	double _chi2ThresholdOffsetEE; //chi2 square thr for the Endcap --- Added
	unsigned int _minEntries; ///< require a minimum number of entries in a ring to do averages
	float        _globalOffset;    ///< time to subtract from every event
	bool _storeEvents;
	bool _produceNewCalib; ///< true if you don't want to use the values in DB and what to extract new absolute calibrations, if false iteration does not work
	std::string _outputDumpFileName; ///< name of the output file for the calibration constants' dump
	float _maxSkewnessForDump;
/// @}

	void dumpCalibration(std::string filename);
	void dumpCorrections(std::string filename);

// plotting
///fill histograms with the measured shifts (that will become -corrections for the next step)
	void FillCalibrationCorrectionHists(EcalTimeCalibrationMap::const_iterator cal_itr);
	void FillHWCorrectionHists(EcalTimeCalibrationMap::const_iterator cal_itr);
	void FillEnergyStabilityHists(EcalTimeCalibrationMap::const_iterator cal_itr, std::vector< std::pair<float, EcalCrystalTimingCalibration*> > energyStability);
	void initHists(TFileDirectory dir);
	void initEventHists(TFileDirectory dir);
	void initTree(TFileDirectory dir);

	EcalTimeCalibConstants _timeCalibConstants; ///< container of calibrations updated iter by iter



	/**
	  \brief  If recHit passes the selection it is added to the list of recHits to be used for calibration

	  The recHit is used (accepted) if:
		 - recHit flag in the list of _recHitFlags defined in the config file
		 - recHit energy in EB > _minRecHitEnergy defined in the config file
		 - recHit energy in EE is x2 the threshold of EB
		 - at each iteration the recHit threshold is raised by _minRecHitEnergyStep
		 If the recHit is used, the time information is added to _eventTimeMap
	*/
	bool addRecHit(const EcalRecHit& recHit, EventTimeMap& eventTimeMap_);


	/// Adds the recHit to the per Event histograms
	void plotRecHit(const EcalTimingEvent& recHit);
	///
	/// Returns an EcalTimingEvent with a new time, which has been adjusted
	/// so that the upstream endcap is 0.
	///
	EcalTimingEvent correctGlobalOffset(const EcalTimingEvent& ev, int splashDir, float bunchCorr);

	unsigned int getElecID(DetId id)
	{
		return (elecMap_->getElectronicsId(id).rawId() >> 6) & 0x3FFF;
	}
	float getEnergyThreshold(const DetId detid)
	{
		int iRing = _ringTools.getRingIndexInSubdet(detid);
		if (detid.subdetId() == EcalBarrel) {
			return 13 * 0.04  + _energyThresholdOffsetEB;
		} else {
			return 20 * (79.29 - 4.148 * iRing + 0.2442 * iRing * iRing ) / 1000  + _energyThresholdOffsetEE;
		}
	}
	float getChi2Threshold(const DetId detid)
	{
		if (detid.subdetId() == EcalBarrel) {
			return _chi2ThresholdOffsetEB;
		} else {
			return _chi2ThresholdOffsetEE;
		}
	}

	std::map<DetId, float>  _CrysEnergyMap;

	edm::Service<TFileService> fileService_;
	TFileDirectory histDir_;
	// Tree
	TTree *dumpTree;
	TTree * timingTree;
	TTree * energyStabilityTree;

	// Mean Histograms

	TProfile2D* EneMapEEP_; /// Using TProfile2D so we don't paint empty bins.
	TProfile2D* EneMapEEM_;
	TProfile2D* TimeMapEEP_;
	TProfile2D* TimeMapEEM_;

	TProfile2D* EneMapEB_;
	TProfile2D* TimeMapEB_;

	// Error Histograms
	TProfile2D* TimeErrorMapEEP_;
	TProfile2D* TimeErrorMapEEM_;

	TProfile2D* TimeErrorMapEB_;

	// Event Based Plots
	TProfile2D * Event_EneMapEEP_;
	TProfile2D * Event_EneMapEEM_;
	TProfile2D * Event_EneMapEB_;

	TProfile2D* Event_TimeMapEEP_;
	TProfile2D* Event_TimeMapEEM_;
	TProfile2D* Event_TimeMapEB_;

	TProfile2D* Event_TimeMapEEP_OOT;
	TProfile2D* Event_TimeMapEEM_OOT;
	TProfile2D* Event_TimeMapEB_OOT;

	TH1F* RechitEneEB_;
	TH1F* RechitTimeEB_;
	TH1F* RechitEneEEM_;
	TH1F* RechitTimeEEM_;
	TH1F* RechitEneEEP_;
	TH1F* RechitTimeEEP_;

	// HW Histograms
	TProfile2D* HWTimeMapEEP_;
	TProfile2D* HWTimeMapEEM_;
	TProfile2D* HWTimeMapEB_;

	TH2F* RechitEnergyTimeEB;
	TH2F* RechitEnergyTimeEEM;
	TH2F* RechitEnergyTimeEEP;

	//Occupancy plots
	TH2D* OccupancyEB_;
	TH2D* OccupancyEEM_;
	TH2D* OccupancyEEP_;

	EcalRingCalibrationTools _ringTools;
	const CaloSubdetectorGeometry * endcapGeometry_;
	const CaloSubdetectorGeometry * barrelGeometry_;

	const EcalElectronicsMapping * elecMap_;

	unsigned int _iter;
};

#endif
