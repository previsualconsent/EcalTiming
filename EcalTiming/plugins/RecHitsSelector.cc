// -*- C++ -*-
//
// Package:    EcalTiming/RecHitSelector
// Class:      RecHitSelector
// 
/**\class RecHitSelector RecHitSelector.cc EcalTiming/RecHitSelector/plugins/RecHitSelector.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Peter Hansen
//         Created:  Tue, 21 Jul 2015 09:35:32 GMT
//
//


// system include files
#include <memory>
#include <iostream>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"

//
// class declaration
//

class RecHitSelector : public edm::EDProducer {
   public:
      explicit RecHitSelector(const edm::ParameterSet&);
      ~RecHitSelector();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() override;
      virtual void produce(edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;
      
      //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
      //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

      // ----------member data ---------------------------
		edm::InputTag _ecalRecHitsTAG;
		std::vector<int> _recHitFlags;
		double _minRecHitEnergy;
};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
RecHitSelector::RecHitSelector(const edm::ParameterSet& iConfig):
	_ecalRecHitsTAG(iConfig.getParameter<edm::InputTag>("recHitCollection")),
	_recHitFlags(iConfig.getParameter<std::vector<int> >("recHitFlags")),
	_minRecHitEnergy(iConfig.getParameter<double>("minRecHitEnergy"))
{
   //register your products
   produces<EcalRecHitCollection>();

   //if do put with a label
   //produces<EBRecHitCollection>("filteredRecHitEBCollection");
 
   //if you want to put into the Run
   //produces<ExampleData2,InRun>();
   //now do what ever other initialization is needed
  
}


RecHitSelector::~RecHitSelector()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
RecHitSelector::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
	// here the getByToken of the rechits
	edm::Handle<EcalRecHitCollection> RecHitHandle;
	iEvent.getByLabel(_ecalRecHitsTAG, RecHitHandle);

   std::unique_ptr<EcalRecHitCollection> rec_out(new EcalRecHitCollection());

	for(auto  recHit_itr : *RecHitHandle) {
		if(!recHit_itr.checkFlags(_recHitFlags)) continue;
		if(recHit_itr.energy() < _minRecHitEnergy) continue;

		rec_out->push_back(recHit_itr);
	}

   iEvent.put(std::move(rec_out));

/* this is an EventSetup example
   //Read SetupData from the SetupRecord in the EventSetup
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
*/
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
RecHitSelector::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
RecHitSelector::endJob() {
}

// ------------ method called when starting to processes a run  ------------
/*
void
RecHitSelector::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
RecHitSelector::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
RecHitSelector::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
RecHitSelector::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
RecHitSelector::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("recHitCollection");
  desc.add<std::vector<int> >("recHitFlags");
  desc.add<double>("minRecHitEnergy");
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(RecHitSelector);
