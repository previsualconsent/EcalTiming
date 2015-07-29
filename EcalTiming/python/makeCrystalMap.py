import ROOT
from EcalTiming.EcalTiming.tree2txt import tree2txt
import math

import os
import sys
import errno
import shutil

argc = len(sys.argv)
if argc < 3:
	print "Usage: tree2txt.py input.root path/to/TTree"
	sys.exit(-1)

filename = sys.argv[1]
tree_path = sys.argv[2]

file = ROOT.TFile.Open(filename)
tree = file.Get(tree_path)
tree2txt(tree, filter = ["ix","iy","iz","elecID","iRing","rawid"])


