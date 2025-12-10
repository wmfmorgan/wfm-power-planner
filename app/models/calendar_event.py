# app/models/calendar_event.py
from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    uid = db.Column(db.String(255), nullable=False, unique=True, index=True)  # ICS UID — NO DUPES
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    start_datetime = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    end_datetime = db.Column(db.DateTime(timezone=True))
    all_day = db.Column(db.Boolean, default=False)
    
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.Text)  # Full RRULE string
    recurrence_id = db.Column(db.DateTime(timezone=True))  # For exceptions
    
    location = db.Column(db.String(200))
    source = db.Column(db.String(50), default='outlook_ics')  # For future multi-source
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CalendarEvent {self.title} ({self.uid[:8]})>"