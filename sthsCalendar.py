#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sydney Technical High School Calendar to iCalendar Crawler

Application to create an iCalendar file based of calender information from http://sths.nsw.edu.au/about-sths/calendar

Author: Andrew Wong
(e) featherbear@navhaxs.au.eu.org

Version 1.0

"""

########################## SETTINGS ##########################
_debugPrintEnabled = 1  # Print console output?   (Default: 1)
_output = '/sths.ics'  # File path to write to
########################## SETTINGS ##########################



























# Try to import BeautifulSoup, if not installed, attempt to install
try:
    from bs4 import BeautifulSoup
except ImportError:
    import pip

    pip.main(['install', 'beautifulsoup4'])
    from bs4 import BeautifulSoup
import urllib2, re, json


def main():
    global _debugPrintEnabled
    global _output

    # Print lines
    def debugPrint(line):
        if _debugPrintEnabled:
        	print(str(line))

	# Create Request object with user agent (So we don't get a 403 HTTP error)

	url = urllib2.Request('http://sths.nsw.edu.au/about-sths/calendar',
						  headers={'User-Agent': 'Calendar Crawler (Andrew Wong)/1.0'})
	debugPrint('Opening page: http://sths.nsw.edu.au/about-sths/calendar')

	soup = BeautifulSoup(urllib2.urlopen(url).read(), 'html.parser')  # Open URL
	# Find the next script element which contains the calendar data
	hs = soup.find(id='calendar_container').findNext('script', type="text/javascript").string
	reg = re.search(r"var vjCalEvents = (.*\n\t\t.*);", hs).group(1)  # Extract calendar data
	reg = re.sub(r"(,|{)(\w{2,11})(:)", r'\1"\2"\3', reg)  # Surround properties with double quotations
	debugPrint('Parsing page contents into JSON\n')
	calendar = json.loads(reg)  # Parse string as a JSON object

	"""
	Inside each object
		id - ignoreme
		title - EVENT TITLE
		start - EVENT START
		end - EVENT FINISH (OPTIONAL)
		description - EVENT DESCRIPTION

		allDay - ignoreme (always true)
		url - ignoreme (contains event description (however already in JSON))
		className - ignoreme (...)
	"""

	debugPrint('Generating iCalendar file...\n')

	# Try to import iCalendar, if not installed, attempt to install
	try:
		from icalendar import Calendar, Event
	except ImportError:
		import pip
		pip.main(['install', 'icalendar'])
		from icalendar import Calendar, Event
	from datetime import datetime, timedelta
	from six.moves import html_parser

	ical = Calendar()
	ical.add('prodid', '-//navhaxs.au.eu.org//Sydney Technical High Calendar//EN')
	ical.add('version', '2.0')
	ical.add('x-wr-calname', 'Sydney Technical High High School')
	ical.add('x-wr-timezone', 'Australia/Sydney')
	ical.add('x-wr-caldesc', 'Calendar from information located at http://sths.nsw.edu.au/about-sths/calendar')

	for event in calendar:
		ical_event = Event()
		ical_event.add('summary', html_parser.HTMLParser().unescape(event['title']))
		'description' in event and ical_event.add('description',
							html_parser.HTMLParser().unescape(event['description']))
		date = datetime.strptime(event['start'], '%Y-%m-%d %H:%M:%S').date()
		ical_event.add('dtstart', date)
		ical_event.add('dtend', (datetime.strptime(event['end'], '%Y-%m-%d %H:%M:%S').date() if 'end' in event
								 else date + timedelta(days=1)))
		ical.add_component(ical_event)

	debugPrint('Writing iCalender file...')
	with open(_output, 'wb') as f:
		f.write(ical.to_ical())

	debugPrint('\nDone!')

main()
