import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, date, timezone

CALENDAR_ID = "c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0@group.calendar.google.com"
FEED_URL = f"https://calendar.google.com/calendar/ical/{urllib.parse.quote(CALENDAR_ID, safe='')}/public/full.ics"
OUT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "_data", "calendar_events.json"))
MAX_EVENTS = 30


def unfold(lines):
    unfolded = []
    for line in lines:
        if line.startswith(" ") or line.startswith("\t"):
            if unfolded:
                unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return unfolded


def parse_property(line):
    if ":" not in line:
        return None, [], ""
    name_params, value = line.split(":", 1)
    parts = name_params.split(";")
    name = parts[0]
    params = parts[1:]
    return name, params, value


def parse_dt(value, params):
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    tzid = None
    for param in params:
        if param.startswith("TZID="):
            tzid = param.split("=", 1)[1]
            break

    if re.fullmatch(r"\d{8}", value):
        return date.fromisoformat(value)

    try:
        dt = datetime.strptime(value, "%Y%m%dT%H%M%S")
        if tzid:
            try:
                from zoneinfo import ZoneInfo

                dt = dt.replace(tzinfo=ZoneInfo(tzid))
            except Exception:
                pass
        return dt
    except ValueError:
        pass

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def normalize_value(value):
    return value.replace("\\n", "\n").strip()


def sort_key(value):
    if not value:
        return "9999-12-31T23:59:59"
    return str(value)


def is_future(value):
    if not value:
        return False
    now = datetime.now(timezone.utc)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value) >= now.date()
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= now
    except ValueError:
        return False


def convert_to_output(event):
    output = {
        "summary": event.get("summary", "Untitled event"),
        "start": event.get("start"),
    }
    if event.get("location"):
        output["location"] = event["location"]
    if event.get("description"):
        output["description"] = event["description"]
    if event.get("url"):
        output["url"] = event["url"]
    return output


def main():
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        text = response.read().decode("utf-8", errors="replace")

    lines = unfold(text.splitlines())
    events = []
    current = None

    for line in lines:
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT" and current is not None:
            if current.get("start") and is_future(current["start"]):
                events.append(current)
            current = None
            continue

        if current is None:
            continue

        name, params, value = parse_property(line)
        if name == "SUMMARY":
            current["summary"] = normalize_value(value)
        elif name == "LOCATION":
            current["location"] = normalize_value(value)
        elif name == "DESCRIPTION":
            current["description"] = normalize_value(value)
        elif name == "URL":
            current["url"] = normalize_value(value)
        elif name == "DTSTART":
            dt = parse_dt(value, params)
            if isinstance(dt, date) and not isinstance(dt, datetime):
                current["start"] = dt.isoformat()
            elif isinstance(dt, datetime):
                current["start"] = dt.isoformat()
        elif name == "DTEND":
            dt = parse_dt(value, params)
            if isinstance(dt, datetime):
                current["end"] = dt.isoformat()
            elif isinstance(dt, date):
                current["end"] = dt.isoformat()

    events = sorted(events, key=lambda event: sort_key(event.get("start")))[:MAX_EVENTS]
    output = [convert_to_output(event) for event in events]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as out_file:
        json.dump(output, out_file, ensure_ascii=False, indent=2)

    print(f"Wrote {len(output)} event(s) to {OUT_PATH}")


if __name__ == "__main__":
    main()
