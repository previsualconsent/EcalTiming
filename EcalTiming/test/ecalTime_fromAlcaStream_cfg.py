import FWCore.ParameterSet.Config as cms
import os, sys, imp, re
import FWCore.ParameterSet.VarParsing as VarParsing

#sys.path(".")

#new options to make everything easier for batch

############################################################
### SETUP OPTIONS

options = VarParsing.VarParsing('standard')
options.register('jsonFile',
                 "",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "path and name of the json file")
options.register('step',
                 "RECOTIMEANALYSIS",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Do reco, time analysis or both, RECO|TIMEANALYSIS|RECOTIMEANALYSIS")
options.register('offset',
                 0.0,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "add this to each crystal time")
options.register('isSplash',
                 0,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "0=false, 1=true"
                 )
options.register('streamName',
                 'AlCaPhiSym',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "type of stream: AlCaPhiSym or AlCaP0")
                 
### setup any defaults you want
options.output="output/ecalTiming.root"
options.secondaryOutput="ntuple.root"

if(options.streamName=="AlCaP0"): options.files = "/store/data/Commissioning2015/AlCaP0/RAW/v1/000/246/342/00000/048ECF48-F906-E511-95AC-02163E011909.root"
elif(options.streamName=="AlCaPhiSym"): options.files = "/store/data/Commissioning2015/AlCaPhiSym/RAW/v1/000/244/768/00000/A8219906-44FD-E411-8DA9-02163E0121C5.root"
else: 
    print "stream ",options.streamName," not foreseen"
    exit
options.maxEvents = -1 # -1 means all events
### get and parse the command line arguments
options.parseArguments()
print options

processname = options.step

doReco = True
doAnalysis = True
if "RECO" not in processname:
	doReco = False
if "TIME" not in processname:
	doAnalysis = False

process = cms.Process(processname)

process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(10000)

process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')

if(options.isSplash==1):
    ## Get Cosmic Reconstruction
    process.load('Configuration/StandardSequences/ReconstructionCosmics_cff')
    process.caloCosmics.remove(process.hbhereco)
    process.caloCosmics.remove(process.hcalLocalRecoSequence)
    process.caloCosmics.remove(process.hfreco)
    process.caloCosmics.remove(process.horeco)
    process.caloCosmics.remove(process.zdcreco)
    process.caloCosmics.remove(process.ecalClusters)
    process.caloCosmicOrSplashRECOSequence = cms.Sequence(process.caloCosmics )#+ process.egammaCosmics)
else:
    process.load('Configuration/StandardSequences/Reconstruction_cff')
    process.recoSequence = cms.Sequence(process.calolocalreco )#+ process.egammaCosmics)

#process.load('PhiSym.EcalCalibAlgos.ecalPhiSymLocarecoWeights_cff')
#process.load('RecoLocalCalo.Configuration.ecalLocalRecoSequence_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('EcalTiming.EcalTiming.ecalLocalRecoSequenceAlCaStream_cff')

if(options.streamName=="AlCaP0"):
    process.ecalMultiFitUncalibRecHit.EBdigiCollection = cms.InputTag("hltAlCaPi0EBRechitsToDigis","pi0EBDigis")
    process.ecalMultiFitUncalibRecHit.EEdigiCollection = cms.InputTag("hltAlCaPi0EERechitsToDigis","pi0EEDigis")
else:
    process.ecalMultiFitUncalibRecHit.EBdigiCollection = cms.InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEB")
    process.ecalMultiFitUncalibRecHit.EEdigiCollection = cms.InputTag("hltEcalPhiSymFilter","phiSymEcalDigisEE")


## Raw to Digi
process.load('Configuration/StandardSequences/RawToDigi_Data_cff')

## HLT Filter Splash
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.spashesHltFilter = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone(
    throw = cms.bool(False),
    HLTPaths = ['HLT_EG20*', 'HLT_SplashEcalSumET', 'HLT_Calibration','HLT_EcalCalibration','HLT_HcalCalibration','HLT_Random','HLT_Physics','HLT_HcalNZS','HLT_SplashEcalSumET','HLTriggerFinalPath' ]
)


## GlobalTag Conditions Related
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'GR_P_V56', '') #run2_data', '')

## Process Digi To Raw Step
process.digiStep = cms.Sequence(process.ecalDigis  + process.ecalPreshowerDigis)

## Process Reco






### Print Out Some Messages
process.MessageLogger = cms.Service("MessageLogger",
    cout = cms.untracked.PSet(
        threshold = cms.untracked.string('WARNING')
    ),
    categories = cms.untracked.vstring('ecalTimeTree'),
    destinations = cms.untracked.vstring('cout')
)

# enable the TrigReport and TimeReport
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
#    SkipEvent = cms.untracked.vstring('ProductNotFound')
)

# dbs search --query "find file where dataset=/ExpressPhysics/BeamCommissioning09-Express-v2/FEVT and run=124020" | grep store | awk '{printf "\"%s\",\n", $1}'
# Input source
process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
 	 fileNames = cms.untracked.vstring(options.files),
)

if(len(options.jsonFile) > 0):
	import FWCore.PythonUtilities.LumiList as LumiList
	process.source.lumisToProcess = LumiList.LumiList(filename = options.jsonFile).getVLuminosityBlockRange()



# Output definition
process.RECOoutput = cms.OutputModule("PoolOutputModule",
splitLevel = cms.untracked.int32(0),
eventAutoFlushCompressedSize = cms.untracked.int32(5242880),
outputCommands = cms.untracked.vstring('drop *',"keep *_ecalRecHit_EcalRecHits*_*"),
fileName = cms.untracked.string(options.output),
dataset = cms.untracked.PSet(
   filterName = cms.untracked.string(''),
   dataTier = cms.untracked.string('RECO')
)
)


## Histogram files
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string(options.output),
                                   closeFileFast = cms.untracked.bool(True)
                                   )

### NumBer of events
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxEvents))


process.filter=cms.Sequence()
if(options.isSplash==1):
    process.filter+=process.spashesHltFilter
    process.reco_step = cms.Sequence(process.caloCosmicOrSplashRECOSequence)
else:
    #process.reco_step = cms.Sequence(process.reconstruction_step_multiFit)
    process.reco_step = cms.Sequence(process.ecalLocalRecoSequenceAlCaStream)

### Process Full Path
if(options.isSplash==0):
    process.digiStep = cms.Sequence()



evtPlots = True if options.isSplash else False


#import Electronics mapping
process.load("Geometry.EcalCommonData.EcalOnly_cfi")
process.load("Geometry.EcalMapping.EcalMapping_cfi")
process.load("Geometry.EcalMapping.EcalMappingRecord_cfi")
#process.load("Geometry.CaloEventSetup.CaloGeometry_cff")

#ESLooperProducer looper is imported here:
process.load('EcalTiming.EcalTiming.ecalTimingCalibProducer_cfi')
process.timing.isSplash= cms.bool(True if options.isSplash else False)
process.timing.makeEventPlots=evtPlots
process.timing.globalOffset = cms.double(options.offset)
process.timing.outputDumpFile = process.TFileService.fileName
process.timing.minRecHitEnergy = cms.double(0.5)


process.analysis = cms.Sequence( process.timing )
process.reco = cms.Sequence( process.filter 
                      + process.digiStep 
                      + process.reco_step
                      )


process.seq = cms.Sequence()
if doReco:
	process.seq += process.reco
if doAnalysis:
	process.seq += process.analysis
else:
	process.endp = cms.EndPath(process.RECOoutput)

process.p = cms.Path(process.seq)

#process.schedule = cms.Schedule(process.p, process,enp)

processDumpFile = open('processDump.py', 'w')
print >> processDumpFile, process.dumpPython()
