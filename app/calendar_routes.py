# app/calendar_routes.py
# CALENDAR COMMAND CENTER — PHASE 2 BEGINS
from flask import Blueprint, render_template, jsonify, request, make_response
from flask_login import login_required, current_user
from app.extensions import db
from app.services.calendar_service import import_ics_events
import os
import requests
from datetime import datetime, date, timedelta
from dateutil.rrule import rrulestr
from dateutil.tz import tzutc
from pytz import timezone
import re
import logging

calendar_bp = Blueprint('calendar', __name__, template_folder='templates/calendar')

@calendar_bp.route('/calendar')
@calendar_bp.route('/calendar/<view>')
@calendar_bp.route('/calendar/<view>/<int:year>')
@calendar_bp.route('/calendar/<view>/<int:year>/<int:month>')
@calendar_bp.route('/calendar/<view>/<int:year>/<int:month>/<int:day>')
@login_required
def calendar_view(view='month', year=None, month=None, day=None):
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    day = day or today.day

    valid_views = ['year', 'quarter', 'month', 'week', 'day']
    if view not in valid_views:
        view = 'month'

    context = {
        'current_view': view,
        'year': year,
        'month': month,
        'day': day,
        'today': today,
        'datetime': datetime,
    }
    # ADD THESE LINES — THIS IS THE FIX
    response = make_response(render_template('calendar/base_calendar.html', **context))
    response.headers.set('X-Current-View', view)
    response.headers.set('X-Current-Year', str(year))
    response.headers.set('X-Current-Month', str(month))
    response.headers.set('X-Current-Day', str(day))
    return response

@calendar_bp.route('/api/import-calendar', defaults={'datestr': None})
@calendar_bp.route('/api/import-calendar/<datestr>')
def import_calendar(datestr):
    print(datestr)
    target_date = date.today()
    if datestr and len(datestr) == 8 and datestr.isdigit():
        try:
            target_date = date(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:8]))
        except:
            return jsonify({'success': False, 'error': 'Bad date'}), 400

    ics_url = os.getenv('ICS_CALENDAR_URL', '').split('?')[0]

    try:
        response = requests.get(ics_url, timeout=30)
        response.raise_for_status()
        ics_content = response.text

        # ———— REUSE YOUR WORKING SCRIPT LOGIC 100% ————

        central = timezone("America/Chicago")

        # Your exact _parse_dt from the working script
        _OUTLOOK_TZ_MAP = {
            "Eastern Standard Time": "America/New_York",
            "Eastern Daylight Time": "America/New_York",
            "Central Standard Time": "America/Chicago",
            "Central Daylight Time": "America/Chicago",
            "Pacific Standard Time": "America/Los_Angeles",
            "Mountain Standard Time": "America/Denver",
            "India Standard Time": "Asia/Kolkata",
        }

        def _parse_dt(val, tzid=None, is_date=False):
            val = val.split(':')[-1]
            val = val[:-1] if val.endswith('Z') else val
            if is_date or len(val) == 8:
                return datetime.strptime(val, "%Y%m%d").date()
            dt = datetime.strptime(val[:15], "%Y%m%dT%H%M%S")
            if tzid and tzid in _OUTLOOK_TZ_MAP:
                tz = timezone(_OUTLOOK_TZ_MAP[tzid])
                dt = tz.localize(dt)
            elif val.endswith('Z'):
                dt = dt.replace(tzinfo=tzutc())
            else:
                dt = timezone("America/Chicago").localize(dt)
            return dt.astimezone(central)

        def _compute_end(start, end_dt, duration):
            central = timezone("America/Chicago")
            if end_dt:
                if end_dt.tzinfo is None:
                    end_dt = central.localize(end_dt)
                return end_dt.astimezone(central)
            if duration:
                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration)
                if match:
                    h = int(match.group(1) or 0)
                    m = int(match.group(2) or 0)
                    return start + timedelta(hours=h, minutes=m)
            return start + timedelta(hours=1)

        def _to_date(dt):
            return dt.date() if hasattr(dt, 'date') else dt

        # Parse all events exactly like your script
        all_events = []
        lines = [l.rstrip() for l in ics_content.replace('\r\n', '\n').split('\n')]
        i = 0
        in_event = False
        event = None

        while i < len(lines):
            line = lines[i]
            while i + 1 < len(lines) and lines[i + 1].startswith((' ', '\t')):
                i += 1
                line += lines[i][1:].lstrip()

            if line == "BEGIN:VEVENT":
                event = {
                    "UID": None, "SUMMARY": "", "DTSTART": None, "DTEND": None,
                    "DURATION": None, "RRULE": None, "EXDATE": [], 
                    "LOCATION": "", "DESCRIPTION": "", "AllDay": False,
                    "RECURRENCE-ID": None,
                }
                in_event = True

            elif line == "END:VEVENT" and in_event:
                all_events.append(event.copy())
                in_event = False

            elif in_event and ':' in line:
                key_part, value = line.split(':', 1)
                params = {}
                if ';' in key_part:
                    key = key_part.split(';')[0]
                    param_str = ';' + key_part[len(key):]
                    for m in re.finditer(r';([^=;]+)=([^;]+)', param_str):
                        params[m.group(1)] = m.group(2)
                else:
                    key = key_part

                value = value.replace('\\n', '\n').replace('\\,', ',').replace('\\;', ';')

                if key == "SUMMARY": event["SUMMARY"] = value
                elif key == "LOCATION": event["LOCATION"] = value
                elif key == "DESCRIPTION": event["DESCRIPTION"] = value
                elif key == "UID": event["UID"] = value
                elif key == "RRULE": event["RRULE"] = value
                elif key == "EXDATE":
                    for ex in value.split(','):
                        event["EXDATE"].append(_parse_dt(ex))
                elif key == "DTSTART":
                    event["DTSTART"] = _parse_dt(value, params.get("TZID"), "VALUE=DATE" in key_part)
                    event["AllDay"] = "VALUE=DATE" in key_part
                elif key == "DTEND":
                    event["DTEND"] = _parse_dt(value, params.get("TZID"), "VALUE=DATE" in key_part)
                elif key == "DURATION": event["DURATION"] = value
                elif key == "RECURRENCE-ID":
                    event["RECURRENCE-ID"] = _parse_dt(value, params.get("TZID"))

            i += 1

        # Build exceptions map
        exceptions = {}
        for e in all_events:
            if e["RECURRENCE-ID"]:
                uid = e["UID"]
                exc_date = _to_date(e["RECURRENCE-ID"])
                exceptions.setdefault(uid, set()).add(exc_date)

        # Final processing — exactly like your script
        imported_events = []
        for e in all_events:
            start = e["DTSTART"]
            if not start:
                continue

            if e["RECURRENCE-ID"]:
                if _to_date(start) == target_date:
                    imported_events.append(e.copy())
                continue

            if not e["RRULE"]:
                if _to_date(start) == target_date:
                    imported_events.append(e.copy())
                continue

            try:
                base_start = start.replace(tzinfo=tzutc()) if start.tzinfo is None else start
                rule = rrulestr(e["RRULE"], dtstart=base_start)
                window_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=tzutc())
                window_end = window_start + timedelta(days=1)

                for inst_start in rule.between(window_start, window_end, inc=True):
                    inst_date = inst_start.date()
                    uid = e["UID"]

                    if uid in exceptions and inst_date in exceptions[uid]:
                        continue
                    if any(_to_date(ex) == inst_date for ex in e["EXDATE"]):
                        continue

                    inst_end = _compute_end(inst_start, e["DTEND"], e["DURATION"])
                    new_e = e.copy()
                    new_e["DTSTART"] = inst_start
                    new_e["DTEND"] = inst_end
                    imported_events.append(new_e)

            except Exception as ex:
                print(f"RRULE FAILED → {e.get('SUMMARY', 'Unknown')}: {ex}")

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    result = import_ics_events(imported_events)
    
    return jsonify({
        'success': True,
        'imported': result['imported'],
        'skipped': result['skipped'],
        'message': f"ICS import complete — {result['imported']} new events added!"
    })