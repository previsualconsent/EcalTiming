from RecoLocalCalo.Configuration.ecalLocalRecoSequence_cff import *

ecalLocalRecoSequenceAlCaP0Stream = cms.Sequence (ecalMultiFitUncalibRecHit * 
                                                        ecalRecHit)

ecalMultiFitUncalibRecHit.EBdigiCollection = cms.InputTag("dummyHits","dummyBarrelDigis")
ecalMultiFitUncalibRecHit.EEdigiCollection = cms.InputTag("dummyHits","dummyEndcapDigis")


#ecalDetIdToBeRecovered =  RecoLocalCalo.EcalRecProducers.ecalDetIdToBeRecovered_cfi.ecalDetIdToBeRecovered.clone()
ecalRecHit.killDeadChannels = cms.bool( False )
ecalRecHit.recoverEBVFE = cms.bool( False )
ecalRecHit.recoverEEVFE = cms.bool( False )
ecalRecHit.recoverEBFE = cms.bool( False )
ecalRecHit.recoverEEFE = cms.bool( False )
ecalRecHit.recoverEEIsolatedChannels = cms.bool( False )
ecalRecHit.recoverEBIsolatedChannels = cms.bool( False )
