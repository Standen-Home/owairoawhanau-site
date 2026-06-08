import urllib.request
url = 'https://calendar.google.com/calendar/ical/c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0%40group.calendar.google.com/public/basic.ics'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=20) as r:
    print('status', r.status)
    print('content-type', r.getheader('Content-Type'))
    print('access-control-allow-origin', r.getheader('Access-Control-Allow-Origin'))
    print('preview', r.read(200).decode('utf-8', errors='replace'))
