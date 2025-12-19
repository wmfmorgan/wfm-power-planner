# app/calendar_routes.py
# CALENDAR COMMAND CENTER — PHASE 2 BEGINS
from flask import Blueprint, flash, render_template, jsonify, request, make_response
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
from app.models.task import TaskStatus, TaskPriority, TaskRecurrenceType
from app.services.reflection_service import upsert_note, get_all_for_period
from app.date_utils import get_sunday_of_week, get_first_of_month, get_iso_week_for_goal, get_sunday_of_week, get_first_of_month


calendar_bp = Blueprint('calendar', __name__, template_folder='templates/calendar')

def get_sunday_of_week(year: int, month: int, day: int) -> date:
    d = date(year, month, day)
    return d - timedelta(days=d.weekday() + 1)  # +1 because Monday=0, Sunday=6 → we want Sunday

def get_first_of_month(year: int, month: int) -> date:
    return date(year, month, 1)

@calendar_bp.route('/calendar')
@calendar_bp.route('/calendar/<view>')
@calendar_bp.route('/calendar/<view>/<int:year>')
@calendar_bp.route('/calendar/<view>/<int:year>/<int:month>')
@calendar_bp.route('/calendar/<view>/<int:year>/<int:month>/<int:day>')
@login_required
def calendar_view(view='month', year=None, month=None, day=None):

    from app.models.goal import GoalStatus, GoalCategory, GoalTimeframe

    today = datetime.today()
    year = year or today.year
    month = month or today.month
    day = day or today.day

    # NEW: Universal prev/next navigation — one pattern to rule them all
    prev_nav = next_nav = None
    display_values = {}

    current_date = date(year, month, day)

    if view == 'year':
        prev_year = year - 1
        next_year = year + 1
        prev_nav = {'view': 'year', 'year': prev_year}
        next_nav = {'view': 'year', 'year': next_year}
        display_values['year'] = year

    elif view == 'quarter':
        current_q = ((month - 1) // 3) + 1
        prev_q_date = current_date - timedelta(days=90)  # approx 3 months back
        next_q_date = current_date + timedelta(days=90)
        prev_nav = {'view': 'quarter', 'year': prev_q_date.year, 'month': prev_q_date.month}
        next_nav = {'view': 'quarter', 'year': next_q_date.year, 'month': next_q_date.month}
        display_values['quarter'] = f"Q{current_q}"

    elif view == 'month':
        # Prev month
        prev_month_date = current_date - timedelta(days=15)  # safe middle-of-month jump
        if prev_month_date.month == 12:
            prev_year = prev_month_date.year + 1
            prev_month = 1
        else:
            prev_year = prev_month_date.year
            prev_month = prev_month_date.month + 1 if prev_month_date.month == 12 else prev_month_date.month - 1
        # Next month
        next_month_date = current_date + timedelta(days=15)
        next_year = next_month_date.year
        next_month = 1 if next_month_date.month == 12 else next_month_date.month + 1

        prev_nav = {'view': 'month', 'year': prev_year, 'month': prev_month}
        next_nav = {'view': 'month', 'year': next_year, 'month': next_month}
        display_values['month'] = month

    elif view == 'week':
        current_week_number = get_iso_week_for_goal(year, month, day)
        anchor_date = current_date
        prev_week_anchor = anchor_date - timedelta(days=7)
        next_week_anchor = anchor_date + timedelta(days=7)
        prev_nav = {'view': 'week', 'year': prev_week_anchor.year, 'month': prev_week_anchor.month, 'day': prev_week_anchor.day}
        next_nav = {'view': 'week', 'year': next_week_anchor.year, 'month': next_week_anchor.month, 'day': next_week_anchor.day}
        display_values['week'] = f"Week {current_week_number}"

    elif view == 'day':
        prev_day = current_date - timedelta(days=1)
        next_day = current_date + timedelta(days=1)
        prev_nav = {'view': 'day', 'year': prev_day.year, 'month': prev_day.month, 'day': prev_day.day}
        next_nav = {'view': 'day', 'year': next_day.year, 'month': next_day.month, 'day': next_day.day}
        display_values['day'] = day

    context = {
        'current_view': view,
        'year': year,
        'month': month,
        'day': day,
        'today': today,
        'datetime': datetime,
        'goal_statuses': GoalStatus,
        'goal_categories': GoalCategory,    # ← ADD THIS
        'goal_timeframes': GoalTimeframe,
        'task_statuses': TaskStatus,
        'task_priorities' : TaskPriority,  # ← ADD THIS
        'task_recurrence_types' : TaskRecurrenceType,
        'prev_nav': prev_nav,
        'next_nav': next_nav,
        'display_values': display_values,
        'current_view': view,
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
    
    flash(f"ICS sync complete — {result['imported']} new events added, {result['skipped']} skipped.", 'success')
    return jsonify({
        'success': True,
        'imported': result['imported'],
        'skipped': result['skipped']
    })

from app.services.calendar_service import (
    get_events_for_day, create_manual_event,
    update_event, delete_event
)
from datetime import date

@calendar_bp.route('/api/events/day/<int:year>/<int:month>/<int:day>')
@login_required
def api_events_day(year, month, day):
    target = date(year, month, day)
    events = get_events_for_day(target)
    return jsonify([{
    'id': e.id,
    'title': e.title,
    'start_datetime': e.start_datetime.isoformat(),
    'end_datetime': e.end_datetime.isoformat() if e.end_datetime else None,
    'all_day': e.all_day,
    'source': e.source,
    'uid': e.uid  # ← ADD THIS LINE — THE MISSING PIECE!!!
    } for e in events])

@calendar_bp.route('/api/events', methods=['POST'])
@login_required
def api_create_event():
    data = request.json
    day_date = date(
        int(data['year']),
        int(data['month']),
        int(data['day'])
    )
    event = create_manual_event(
        data['title'],
        data['start_time'],
        data['end_time'],
        day_date
    )
    return jsonify({'success': True, 'id': event.id})

@calendar_bp.route('/api/events/<int:event_id>', methods=['PATCH'])
@login_required
def api_update_event(event_id):
    data = request.json
    day_date = date(
        int(data['year']),
        int(data['month']),
        int(data['day'])
    )
    update_event(event_id, data['title'], data['start_time'], data['end_time'], day_date)
    return jsonify({'success': True})

@calendar_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def api_delete_event(event_id):
    delete_event(event_id)
    return jsonify({'success': True})

@calendar_bp.route('/api/reflections/<timeframe>/<path:date_path>', methods=['GET'])
@login_required
def api_get_reflections(timeframe, date_path):
    # date_path is like "2025-12-16" or "2025/12" or "2025/12/16"
    parts = date_path.split('/')
    if len(parts) == 3:
        year, month, day = map(int, parts)
        day_val = day
    elif len(parts) == 2:
        year, month = map(int, parts)
        day_val = 1
    else:
        return jsonify({'error': 'Invalid date'}), 400

    if timeframe == 'daily':
        date_val = date(year, month, day_val)
    elif timeframe == 'weekly':
        date_val = get_sunday_of_week(year, month, day_val or 1)
    else:  # monthly
        date_val = get_first_of_month(year, month)

    data = get_all_for_period(timeframe, date_val)
    return jsonify(data)

@calendar_bp.route('/api/reflections', methods=['POST'])
@login_required
def api_save_reflection():
    data = request.get_json()
    note_type = data['type']
    timeframe = data['timeframe']
    date_str = data['date']  # 'YYYY-MM-DD'
    content = data['content']
    
    date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
    if timeframe == 'weekly':
        date_val = get_sunday_of_week(date_val.year, date_val.month, date_val.day)
    elif timeframe == 'monthly':
        date_val = get_first_of_month(date_val.year, date_val.month)
    
    upsert_note(note_type, timeframe, date_val, content)
    return jsonify({'status': 'saved'})