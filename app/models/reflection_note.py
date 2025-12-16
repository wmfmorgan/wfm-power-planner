# app/models/reflection_note.py
"""
Reflection Notes — warrior's soul forge, saved forever.
Four sacred zones tied to horizon + date.
Composite PK = blazing fast lookups.
"""
from flask_login import current_user
from app.extensions import db
from datetime import date
from enum import Enum
from sqlalchemy import Enum as SQLEnum     # ← must import this alias

# Define Python enums first (used in service layer later if needed)
class NoteType(str, Enum):
    PREP    = "prep"
    WINS    = "wins"
    IMPROVE = "improve"
    NOTES   = "notes"

class ReflectionTimeframe(str, Enum):
    DAILY   = "daily"
    WEEKLY  = "weekly"
    MONTHLY = "monthly"

# PostgreSQL native ENUMs — Tenet #21 + Alembic-safe pattern
NOTE_TYPE_ENUM = SQLEnum(
    NoteType,
    name="notetype",
    values_callable=lambda enum: [e.value for e in enum],
    native_enum=True
)

TIMEFRAME_ENUM = SQLEnum(
    ReflectionTimeframe,
    name="reflectiontimeframe",
    values_callable=lambda enum: [e.value for e in enum],
    native_enum=True
)


class ReflectionNote(db.Model):
    __tablename__ = 'reflection_notes'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    note_type = db.Column(NOTE_TYPE_ENUM, primary_key=True)
    timeframe = db.Column(TIMEFRAME_ENUM, primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    content = db.Column(db.Text, nullable=True, default='')

    user = db.relationship('User', backref=db.backref('reflection_notes', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Reflection {self.note_type} {self.timeframe} {self.date}>'