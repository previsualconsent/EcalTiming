import ROOT
import numpy as np

import sys

#Mapping ROOT types to appropriate python types
int_types = [ "Char_t", "UChar_t","Short_t","UShort_t","Int_t","UInt_t","Long64_t","ULong64_t", "Bool_t"]
float_types = [ "Float_t","Double_t" ]


def tree2txt(tree,filter = []):
	counter = 0
#Get Tree Info
	nevents = tree.GetEntries()
	if filter:
		branches = [ tree.GetBranch(name) for name in filter]
	else:
		branches = [ b for b in tree.GetListOfBranches()]
	columns = dict()
	branch_type = dict()
	branch_format = dict()
	for b in branches:
		branch_type[b] = b.GetListOfLeaves().At(0).GetTypeName()

		if branch_type[b] in int_types:
			b_type = int
			format = "%d"
		elif branch_type[b] in float_types:
			b_type = float
			format = "%.3f"
		else:
			b_type = type(None)
			format = ""

		columns[b] = np.zeros(nevents, dtype=b_type)
		branch_format[b] = format

#Read tree
	for event in tree:
		for b in branches:
			value = event.__getattr__(b.GetName())

			#some code to deal with how root gives us chars
			if(branch_type[b] == "UChar_t"):
				value = ord(value)
			elif(branch_type[b] == "Char_t"):
				value = ord(value)
				if value > 127: 
					value -= 256

			columns[b][counter] = value

		counter += 1
		if counter >= nevents: break

#dump tree
	print '\t'.join( [b.GetName() for b in branches] )
	for i in range(nevents):
		print '\t'.join([ branch_format[b] % columns[b][i] for b in branches])

if __name__ == "__main__":
	#Parse Arguments
	argc = len(sys.argv)
	if argc < 3:
		print "Usage: tree2txt.py input.root path/to/TTree"
		sys.exit(-1)

	filename = sys.argv[1]
	tree_path = sys.argv[2]

	file = ROOT.TFile.Open(filename)
	tree = file.Get(tree_path)
	tree2txt(tree)


