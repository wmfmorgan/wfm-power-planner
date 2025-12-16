# app/services/reflection_service.py
"""
All DB writes for reflection notes go through here — Tenet #17 eternal.
"""
from flask_login import current_user
from app.models.reflection_note import ReflectionNote
from app.extensions import db
from datetime import date

def get_note(user_id, note_type, timeframe, date_val):
    return ReflectionNote.query.get((user_id, note_type, timeframe, date_val))

def upsert_note(note_type: str, timeframe: str, date_val: date, content: str):
    note = get_note(current_user.id, note_type, timeframe, date_val)
    if note is None:
        note = ReflectionNote(
            user_id=current_user.id,
            note_type=note_type,
            timeframe=timeframe,
            date=date_val,
            content=content
        )
        db.session.add(note)
    else:
        note.content = content
    db.session.commit()
    return note

def get_all_for_period(timeframe: str, date_val: date):
    notes = ReflectionNote.query.filter_by(
        user_id=current_user.id,
        timeframe=timeframe,
        date=date_val
    ).all()
    return {note.note_type: note.content or '' for note in notes}