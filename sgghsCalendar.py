#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
St. George Girls High School Calendar to iCalendar Crawler

Application to create an iCalendar file based of calender information from http://sgghs.com.au/news-events/calendar

Author: Andrew Wong
(e) featherbear@navhaxs.au.eu.org

Version 1.3

"""

########################## SETTINGS ##########################
_page = 1  # Which page to start crawling from    (Default: 1)
_debugPrintEnabled = 1  # Print console output?   (Default: 1)
_output = './sgghs.ics'  # File path to write to
########################## SETTINGS ##########################

























# Try to import BeautifulSoup, if not installed, attempt to install
try:
    from bs4 import BeautifulSoup
except ImportError:
    import pip

    pip.main(['install', 'beautifulsoup4'])
    from bs4 import BeautifulSoup
import urllib2
from calendar import month_name as monthlist


def main():
    '''
    Initialise
    '''
    global _page
    global _debugPrintEnabled
    global _output

    # Print lines
    def debugPrint(line):
        if _debugPrintEnabled:
            print(str(line))

    # Callback 'Exception'
    class CrawlerException(Exception):
        pass

    calendar = []
    # calendar = [{'date': 'YYYYMMDD', 'title': 'TITLE', 'description': 'DESCRIPTION', 'url': 'URL'}, ...]
    # During crawl, _description_ is populated, and _url_ is removed

    '''
    Crawl pages for event title and date
    '''
    try:
        # Variable name refactors:
        #     hc - html_calendar
        #     hcm - html_calendar_month
        #
        #     hcmmi - html_calendar_month_month_int
        #     hcmms - html_calendar_month_month_str
        #     hcmys - html_calendar_month_year_str
        #
        #     hcmc - html_calendar_month_contents
        #     hcmce - html_calendar_month_contents_event
        #     hcmcedda - html_calendar_month_contents_event_date_date_raw
        #     hcmceddp - html_calendar_month_contents_event_date_date_padded


        debugPrint('Crawl Started.')
        while True:
            url = 'http://sgghs.com.au/news-events/calendar/page:' + str(_page)  # Set url to open
            debugPrint('    Opening page: ' + url)
            soup = BeautifulSoup(urllib2.urlopen(url).read(), 'html.parser')  # Open and parse url
            hc = soup.findAll('table', 'calendar')  # Find calendars (month)
            debugPrint('        Found calendars for %s month(s)' % str(len(hc)))
            if len(hc) > 0:  # Check if there are any calendars in the page
                for hcm in hc:
                    debugPrint('            Current Calendar: %s' % hcm.thead.th.getText())
                    hcmmi = list(monthlist).index(hcm.thead.th.getText().split()[0])  # Month integer
                    hcmms = ('0' if len(str(hcmmi)) == 1 else '') + str(hcmmi)  # Month integer as a string with padding
                    hcmys = hcm.thead.th.getText().split()[1]  # Year as string
                    hcmc = hcm.tbody.findAll('tr')  # Find events (table entries)
                    debugPrint('                Calendar has %s event(s)' % len(hcmc))
                    for event in hcmc:
                        hcmce = event.findAll('td')
                        event_title = hcmce[1].getText()  # Event title
                        hcmcedda = hcmce[0].getText().split()[1][:-2]  # Get date (1-31) as string
                        event_date = hcmys + hcmms + ('0' if len(str(hcmcedda)) == 1 else '') + str(
                            hcmcedda)  # YYYYMMDD
                        event_url = hcmce[1].a['href']
                        debugPrint('                    Event: %s\t%s' % (event_date, event_title))
                        debugPrint('                        Event URL: ' + event_url)
                        calendar.append(
                            {'date': event_date, 'title': event_title, 'url': event_url})  # Add to cal array
                debugPrint('    Crawling next page...')
                _page += 1
            else:
                raise (CrawlerException())  # No more entries! Move on.
    except CrawlerException:
        debugPrint('Initial Crawl Finished.\nRetrieving event descriptions...')
        for i in (xrange(len(calendar))):
            url = 'http://sgghs.com.au' + calendar[i]['url']  # Set url to open
            debugPrint('    Opening page: ' + url)
            soup = BeautifulSoup(urllib2.urlopen(url).read(), 'html.parser')  # Open and parse url
            debugPrint('        Extracting description information')
            event_description = soup.findAll(class_='content')[0].p.getText().encode(
                'utf-8').strip()  # Extract text
            debugPrint('        Description: ' + event_description.replace('\n', '\n                     '))
            calendar[i]['description'] = event_description.replace("\xc2\xa0", ' ').strip()  # Add to event's dictionary
            del calendar[i]['url']  # Delete _url_ from the event's dictionary
        debugPrint('Description Crawl Finished.\n')

        import os.path, ast
        _output_data_ = _output + '.data'
        if os.path.isfile(_output_data_):
            debugPrint('Merging with old calendar data...\n')
            try:
                with open(_output_data_, 'r+') as f:
                    oldCalendar = ast.literal_eval(f.read())
                for event in calendar:
                    if event not in oldCalendar:
                        oldCalendar.append(event)
                calendar = oldCalendar
            except:
                pass
        
        '''
        Generate iCalendar file
        '''
        debugPrint('Generating iCalendar file...\n')

        # Try to import iCalendar, if not installed, attempt to install
        try:
            from icalendar import Calendar, Event
        except ImportError:
            import pip
            pip.main(['install', 'icalendar'])
            from icalendar import Calendar, Event
        from datetime import datetime, timedelta
        import re

        ical = Calendar()
        ical.add('prodid', '-//navhaxs.au.eu.org//St George Girls High Calendar//EN')
        ical.add('version', '2.0')
        ical.add('x-wr-calname', 'St George Girls High School')
        ical.add('x-wr-timezone', 'Australia/Sydney')
        ical.add('x-wr-caldesc', 'Calendar from information located at http://sgghs.com.au/news-events/calendar')

        for event in calendar:
            ical_event = Event()
            ical_event.add('summary', event['title'])
            ical_event.add('description', event['description'])
            date = datetime.strptime(event['date'], '%Y%m%d').date()
            ical_event.add('dtstart', date)
            regexMatch = re.search(r'\sto\s(\w*)\s(\d{1,2})\w{0,2}\s?(\w*)', event['description'])
            try:
                ical_event.add('dtend', datetime.strptime(regexMatch.group(3) if regexMatch.group(1).endswith('day') else regexMatch.group(1), '%B').replace(year=date.year, day=int(regexMatch.group(2))).date() + timedelta(days=1))
            except:
                ical_event.add('dtend', date + timedelta(days=1))
            ical.add_component(ical_event)

        debugPrint('Writing iCalender file...')
        with open(_output, 'wb') as f:
            f.write(ical.to_ical())

        with open(_output_data_, 'wb') as f:
            f.write(str(calendar))

        debugPrint('\nDone!')
        



main()
