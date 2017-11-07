import csv
import os

csv.register_dialect("space", delimiter=" ", skipinitialspace=True)

class Database:
	def __init__(self, filename, sort_field = None, headers = None, dialect = None, protected = False):
		self.db = {}
		self.filename = filename
		self.sort_field = sort_field
		self.headers = headers
		self.rows = []
		self.protected = protected
		if not dialect:
			self.dialect = "space"
		else:
			self.dialect = dialect

		try:
			with open(filename,'r') as csvfile:
				reader = csv.DictReader(csvfile, dialect=self.dialect)
				self.headers = reader.fieldnames
				if not self.sort_field: 
					self.sort_field = reader.fieldnames[0]
				for row in reader:
					self.db[row[self.sort_field]] = row
					self.rows.append( row[self.sort_field] )
		except IOError as e:
			if not self.headers:
				raise ValueError("Database: Must define headers for new file")
			if not self.sort_field:
				self.sort_field = headers[0]

	def get(self, row, field = None):
		if field:
			return self.db[row][field]
		else:
			return self.db[row]

	def set(self, row_name, entries):
		if row_name in self.db:
			row = self.db[row_name]
		else:
			self.rows.append(row_name)
			row = {self.sort_field:row_name}
		try:
			for key in entries:
				row[key] = entries[key]
				if key not in self.headers:
					self.headers.append(key)
		except TypeError:
			for key,entry in zip(self.headers, entries):
				row[key] = entry

		self.db[row_name] = row
		
	def setEntry(self, row_name, field_name, value):
		self.set(row_name, {field_name:value})

	def write(self):
		if self.protected:
			raise RuntimeError("Tried to write to protected db file")
		with open(self.filename, 'w') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = self.headers, dialect = self.dialect, restval="-")
			writer.writeheader()
			for row in sorted(self.rows):
				writer.writerow(self.db[row])

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("filename")
	parser.add_argument("action")
	parser.add_argument("args", nargs="+")
	args = parser.parse_args()
	if args.action == "headers":
		db = Database(args.filename, headers = args.args)
		db.write()
	elif args.action == 'set':
		db = Database(args.filename)
		row_name = args.args[0]
		try:
			entries = {key:value for key,value in map(lambda x: x.split(','), args.args[1:])}
		except ValueError:
			entries = args.args
		db.set(row_name, entries)
		db.write()
	elif args.action == 'get':
		db = Database(args.filename)
		row_name = args.args[0]
		args = args.args[1:]
		for arg in args:
			print db.get(row_name, arg)
