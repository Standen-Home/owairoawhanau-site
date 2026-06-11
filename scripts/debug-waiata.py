import urllib.request, urllib.parse, re
from datetime import datetime, date, timezone

CALENDAR_ID = 'c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0@group.calendar.google.com'
FEED_URL = f'https://calendar.google.com/calendar/ical/{urllib.parse.quote(CALENDAR_ID, safe='')}/public/full.ics'

request = urllib.request.Request(FEED_URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(request, timeout=20) as response:
    text = response.read().decode('utf-8', errors='replace')

lines = text.splitlines()
in_vevent = False
current_event = {}
all_events = []

for i, line in enumerate(lines):
    if line == "BEGIN:VEVENT":
        in_vevent = True
        current_event = {}
    elif line == "END:VEVENT" and in_vevent:
        all_events.append(current_event)
        in_vevent = False
    elif in_vevent:
        if line.startswith("SUMMARY:"):
            current_event['summary'] = line.replace("SUMMARY:", "")
        elif line.startswith("DTSTART"):
            current_event['dtstart'] = line

print("=== ALL EVENTS WITH DTSTART ===")
for event in all_events:
    if event.get('dtstart'):
        print(f"{event.get('summary', 'NO SUMMARY')}: {event['dtstart']}")
    
print("\n=== WAIATA-RELATED EVENTS ===")
for event in all_events:
    summary = event.get('summary', '').lower()
    if 'waiata' in summary or 'ō wairoa' in summary:
        print(f"{event.get('summary')}: {event.get('dtstart')}")
