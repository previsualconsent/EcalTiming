#!/usr/bin/python
import sys
from bs4 import BeautifulSoup
from datetime import datetime

epoch = datetime.utcfromtimestamp(0)

filename = sys.argv[1]

html_doc = ''.join(open(filename,'r').readlines())
soup = BeautifulSoup( html_doc.replace("&nbsp;",""))

headers = [str(header.contents[0]) for header in soup.find_all("th")]

myheaders = ["RUN","STARTTIME","STOPTIME"]
myheaders_index = [headers.index(h) for h in myheaders]

for h in myheaders:
	print h,
print

for row in soup.tbody.find_all("tr"):
	cells = [td.contents[0].string for td in row.find_all("td")]
	for i in myheaders_index:
		if headers[i] in ["STARTTIME","STOPTIME"]:
			dt = (datetime.strptime(cells[i], "%Y.%m.%d %H:%M:%S") - epoch)
			print dt.seconds + dt.days * 86400,
		else:
			print cells[i],
	print

