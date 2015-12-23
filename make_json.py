import xml.etree.ElementTree
import datetime
import parsedatetime
import json
import os.path
import sys

format = "%Y-%m-%d"
null_date = "0000-00-00"

def format_date(date):
	return  date[5:7] + '/' + date[8:] + '/' + date[2:4]


def fix_date(date):
	"""Fix malformed date such as "2015-00-00" to "2015-01-01"

	Assumes year is valid.

	Args:
		date (str): Date

	Returns:
		str: valid date
	"""

	if date == null_date:
		return null_date

	m = date[5:7]
	if m == '00': m = '01'
	d = date[8:]
	if d == '00': d = '01'

	return date[:5] + m + '-' + d
#End fix_date

def ff_date(date):

	return format_date(fix_date(date))


def compare_date(d1, d2, find_max=True):
	"""Compare two animelist dates

	Args:
		d1, d2 (str): Dates from animelist xml
		find_max (Optional[bool]): Return max
	Returns:
		str: The min/max date. May be altered to form a valid date
	"""
	if d1 == null_date and d2 == null_date:
		return null_date
	elif d1 == null_date:
		return fix_date(d2)
	elif d2 == null_date:
		return fix_date(d1)

	d1 = fix_date(d1)
	d2 = fix_date(d2)
	if d1 == d2:
		return d1
	dt1 = datetime.datetime.strptime(d1, format)
	dt2 = datetime.datetime.strptime(d2, format)

	var = dt1 > dt2
	if (find_max and var) or (not find_max and not var):
		return d1
	else:
		return d2


#end compare_date


def make_json(filename, out=None):
	"""Generate timeline json from animelist xml. Outputs to standard out.

	Args:
		filename (str): Path to xml file
		out (str): Output json file name

	"""
	first_date = null_date
	last_date = null_date
	dated_anime = []
	not_dated_anime = []
	tree = xml.etree.ElementTree.parse(filename)
	
	#find anime with watch dates
	for anime in tree.findall('anime'):
		if anime.find('my_status').text != "Completed":
			continue

		start = fix_date(anime.find('my_start_date').text)
		end = fix_date(anime.find('my_finish_date').text)
		if start == null_date and end == null_date:
			not_dated_anime.append(anime)
		else:
			dated_anime.append(anime)

		

		first_date = compare_date(first_date, start, False)
		last_date = compare_date(last_date, end)

	#endfor

	data = {}
	data['tick_format'] = format
	data['width'] = 1000
	data['start'] = format_date(first_date)
	data['end'] = format_date(last_date)
	callouts = []

	#make callouts
	for anime in dated_anime:
		c = []
		d = []

		start = anime.find('my_start_date').text
		end = anime.find('my_finish_date').text
		name = anime.find('series_title').text

		#one date
		if start == end or start == null_date or end == null_date:
			date = None 
			if start != null_date:
				date = start
			else:
				date = end
			date = ff_date(date)
			c.append(name)
			c.append(date)
			callouts.append(c)
		#end one date
		#2 date
		else:

			blueish = "#C0C0FF"
			redish = "#CD3F85"
			start = ff_date(start)
			end = ff_date(end)
			start_lable = "Started " + name
			finish_lable = "Finished " + name

			c.append(start_lable)
			c.append(start)
			c.append(blueish)
			callouts.append(c)
			d.append(finish_lable)
			d.append(end)
			d.append(redish)
			callouts.append(d)

		#end 2 date
		
	#end callouts
	
	data['callouts'] = callouts

	json_data = json.dumps(data)

	print json_data

#end makejson




def usage():
	print 'Usage: `python make_json.py animelist.xml list.json'
	sys.exit(-1)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'missing input filename'
		usage()
	filename = sys.argv[1]
	if not os.path.isfile(filename):
		print 'file %s not found' % filename
		sys.exit(-1)

	out = None
	if len(sys.argv) >2 :
		out = sys.argv[2]
	#timeline = Timeline(sys.argv[1])
	#timeline.build()
	#print timeline.to_string()
	make_json(filename, out)