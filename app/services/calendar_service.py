# app/services/calendar_service.py
from app.extensions import db
from app.models.calendar_event import CalendarEvent
from flask_login import current_user
from datetime import datetime, date, timedelta
import logging

def import_ics_events(parsed_events, source_date=None):
    """
    TENET #17 — ALL DB WRITES THROUGH SERVICE LAYER
    parsed_events: list of dicts from your ICS parser
    """
    imported = 0
    skipped = 0

    for ev in parsed_events:
        uid = ev["UID"]
        if not uid:
            logging.warning("Event missing UID — skipping")
            skipped += 1
            continue

        # UPSERT — NO DUPES EVER
        existing = CalendarEvent.query.filter_by(user_id=current_user.id, uid=uid).first()
        if existing:
            skipped += 1
            continue  # Already imported — perfect

        try:
            event = CalendarEvent(
                user_id=current_user.id,
                uid=uid,
                title=ev["SUMMARY"] or "No Title",
                description=ev.get("DESCRIPTION"),
                location=ev.get("LOCATION"),
                start_datetime=ev["DTSTART"],
                end_datetime=ev.get("DTEND"),
                all_day=ev["AllDay"],
                is_recurring=bool(ev.get("RRULE")),
                recurrence_rule=ev.get("RRULE"),
                source='outlook_ics'
            )
            db.session.add(event)
            imported += 1
        except Exception as e:
            logging.error(f"Failed to save event {uid}: {e}")
            skipped += 1

    db.session.commit()
    return {'imported': imported, 'skipped': skipped}

import uuid
from datetime import datetime

def get_events_for_day(target_date):
    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())
    return CalendarEvent.query.filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_datetime >= start,
        CalendarEvent.start_datetime <= end
    ).order_by(CalendarEvent.start_datetime).all()

def create_manual_event(title, start_str, end_str, day_date):
    start_dt = datetime.combine(day_date, datetime.strptime(start_str, "%H:%M:%S").time())
    end_dt = datetime.combine(day_date, datetime.strptime(end_str, "%H:%M:%S").time())
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    event = CalendarEvent(
        user_id=current_user.id,
        uid=str(uuid.uuid4()),
        title=title or "Untitled Event",
        start_datetime=start_dt,
        end_datetime=end_dt,
        source='manual'
    )
    db.session.add(event)
    db.session.commit()
    return event

def update_event(event_id, title, start_str, end_str, day_date):
    event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    event.title = title or "Untitled Event"
    event.start_datetime = datetime.combine(day_date, datetime.strptime(start_str, "%H:%M:%S").time())
    event.end_datetime = datetime.combine(day_date, datetime.strptime(end_str, "%H:%M:%S").time())
    db.session.commit()
    return event

def delete_event(event_id):
    event = CalendarEvent.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    db.session.delete(event)
    db.session.commit()

def delete_all_user_calendar_events(user_id): 
    CalendarEvent.query.filter_by(user_id=user_id).delete()
    db.session.commit()