#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

St. George Girls High School Calendar to iCalendar Crawler

Application to create an iCalendar file based of calender information from http://sgghs.com.au/news-events/calendar

Author: Andrew Wong
(e) featherbear@navhaxs.au.eu.org

Version 1.0

"""

######################### SETTINGS #########################
_page = 1 # Which page to start crawling from    (Default: 1)
_deepCrawl = 1 # Crawl entries for description?  (Default: 1)
_debugPrintEnabled = 1 # Print console output?   (Default: 1)
_output = './sgghs.ics' # File path to write to
######################### SETTINGS #########################




























from bs4 import BeautifulSoup
import urllib2
from calendar import month_name as monthlist

def main():
    global _page
    global _deepCrawl
    global _debugPrintEnabled
    global _output

    def debugPrint(line):
        if _debugPrintEnabled:
            print(str(line))

    class CrawlerException(Exception):
        pass

    calendar = []

    try:
        debugPrint('Crawl Started.')
        while True:
            url = "http://sgghs.com.au/news-events/calendar/page:" + str(_page)
            debugPrint("    Opening page: " + url)
            soup = BeautifulSoup(urllib2.urlopen(url).read(), "html.parser")
            html_calendar = soup.findAll('table', "calendar")
            debugPrint("        Found calendars for %s month(s)" % str(len(html_calendar)))
            if len(html_calendar) > 0:
                for html_calendar_month in html_calendar:
                    debugPrint("            Current Calendar: %s" % html_calendar_month.thead.th.getText())
                    html_calendar_month_month_name = html_calendar_month.thead.th.getText().split()[0]
                    html_calendar_month_month_int = list(monthlist).index(html_calendar_month_month_name)
                    html_calendar_month_month_str = ("0" if len(str(html_calendar_month_month_int))==1 else "") + str(html_calendar_month_month_int)
                    html_calendar_month_year_str = html_calendar_month.thead.th.getText().split()[1]
                    html_calendar_month_contents = html_calendar_month.tbody.findAll('tr')
                    debugPrint("                Calendar has %s event(s)" % len(html_calendar_month_contents))
                    for event in html_calendar_month_contents:
                        html_calendar_month_contents_entry = event.findAll('td')
                        entry_title = html_calendar_month_contents_entry[1].getText()
                        html_calendar_month_contents_entry_date_array = html_calendar_month_contents_entry[0].getText().split()
                        html_calendar_month_contents_entry_date_date_raw = html_calendar_month_contents_entry_date_array[1][:-2]
                        html_calendar_month_contents_entry_date_date_padded = ("0" if len(str(html_calendar_month_contents_entry_date_date_raw))==1 else "") + str(html_calendar_month_contents_entry_date_date_raw)
                        entry_date = html_calendar_month_year_str + html_calendar_month_month_str + html_calendar_month_contents_entry_date_date_padded
                        entry_url = html_calendar_month_contents_entry[1].a['href']
                        debugPrint("                    Entry: %s\t%s" % (entry_date, entry_title))
                        debugPrint('                        Entry URL: ' + entry_url)
                        calendar.append({'date': entry_date, 'title': entry_title, 'url': entry_url})
                debugPrint('    Crawling next page...')
                _page += 1
            else:
                raise(CrawlerException(0))
    except CrawlerException:
        debugPrint('Crawl Finished.\n')
        if _deepCrawl:
            debugPrint('Deep Crawl is enabled! Will retrieve entry description\nDeep Crawl Started.')
            for i in (xrange(len(calendar))):
                url = "http://sgghs.com.au" + calendar[i]['url']
                debugPrint("    Opening page: " + url)
                soup = BeautifulSoup(urllib2.urlopen(url).read(), "html.parser")
                debugPrint("        Extracting description information")
                entry_description = soup.findAll(class_='content')[0].p.getText().encode('utf-8').strip()
                debugPrint("        Description: " + entry_description.replace('\n','\n                     '))
                calendar[i]['description'] = entry_description
                del calendar[i]['url']
            debugPrint("Deep Crawl Finished.\n")
        # Generate the calendar
        debugPrint("Generating iCalendar file...\n")
        from icalendar import Calendar, Event
        from datetime import datetime, timedelta

        ical = Calendar()
        ical.add('prodid', '-//navhaxs.au.eu.org//St. George Girls High Calendar Crawler//EN')
        ical.add('version', '2.0')

        for event in calendar:
            ical_event = Event()
            ical_event.add('summary', event['title'])
            _deepCrawl and ical_event.add('description', event['description'])
            date = datetime.strptime(event['date'], "%Y%m%d").date()
            ical_event.add('dtstart', date)
            ical_event.add('dtend', date + timedelta(days=1))
            ical.add_component(ical_event)

        debugPrint("Writing iCalender file...")
        with open(_output, 'wb') as f:
            f.write(ical.to_ical())

        debugPrint("\nDone!")
main()