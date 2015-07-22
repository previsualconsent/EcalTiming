import FWCore.ParameterSet.Config as cms

filter = cms.EDFilter("EcalTimingCalibProducer",
                    maxLoop = cms.uint32(1),
                    isSplash = cms.bool(False),
                    makeEventPlots = cms.bool(False),
                    recHitEBCollection = cms.InputTag("ecalRecHit","EcalRecHitsEB"),
                    recHitEECollection = cms.InputTag("ecalRecHit","EcalRecHitsEE"),
                    recHitFlags = cms.vint32([0]), # only recHits with these flags are accepted for calibration
                    #recHitMinimumN = cms.uint32(10),
                    recHitMinimumN = cms.uint32(2),
                    minRecHitEnergyStep = cms.double(0.5),
                    minRecHitEnergyNStep = cms.double(10),
                    energyThesholdOffset = cms.double(0.0),
                    minEntries = cms.uint32(1),
                    globalOffset = cms.double(0.),
                    storeEvents = cms.bool(False),
                    produceNewCalib = cms.bool(True),
                    outputDumpFile = cms.string('output.dat'),
                    maxSkewnessForDump = cms.double(2),
                    )
