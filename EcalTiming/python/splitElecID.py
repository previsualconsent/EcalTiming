import os
import sys
argc = len(sys.argv)
if argc < 3:
	print "Usage: splitElecID.py input.txt output.txt"
	sys.exit(-1)

input = sys.argv[1]
output = sys.argv[2]

with open(input, "r") as infile:
   with open(output, "w") as outfile:
      for line in infile:
      	if line[0] == "#":
      		outfile.write(line)
      		continue
      	line = line.split()
      	elecID = int(line[3])
      	outfile.write("\t".join(line[:4] + [str(elecID >> 7), str(elecID & 0x7F)] + line[4:]) + "\n")

