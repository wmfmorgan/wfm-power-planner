# app/services/calendar_service.py
from app.extensions import db
from app.models.calendar_event import CalendarEvent
from flask_login import current_user
from datetime import datetime, date
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