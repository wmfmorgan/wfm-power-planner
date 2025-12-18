# app/services/data_service.py — FULL UNIVERSE DATA OWNERSHIP ETERNAL
"""
TENET #20 — SACRED FULL EMPIRE EXPORT/IMPORT
All tables: goals, tasks, reflections, calendar_events
Atomic transaction — all or nothing
Versioned, safe, rollback eternal
"""
from flask import current_app
from app.extensions import db
from app.models.goal import Goal, GoalTimeframe
from app.models.task import Task, TaskPriority, TaskStatus, TaskRecurrenceType
from app.models.reflection_note import ReflectionNote
from app.models.calendar_event import CalendarEvent
from app.services.goal_service import create_goal_from_dict
from app.services.reflection_service import upsert_note
from datetime import date, datetime

def export_all(user_id, username):
    """Export entire empire — single source of truth"""
    # GOALS — proper nested tree
    root_goals = Goal.query.filter_by(user_id=user_id, parent_id=None).order_by(Goal.sort_order).all()

    def serialize_goal(g):
        return {
            "title": g.title,
            "description": g.description or "",
            "category": g.category.value,
            "status": g.status.value,
            "due_date": g.due_date.isoformat() if g.due_date else None,
            "is_habit": g.is_habit,
            "timeframe": g.timeframe.value,
            "progress": g.progress,  # or calculate_progress()
            "children": [serialize_goal(c) for c in g.children]
        }

    # TASKS — flat
    tasks = Task.query.filter_by(user_id=user_id).all()
    def serialize_task(t):
        return {
            "title": t.title,
            "description": t.description or "",
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "priority": t.priority.value,
            "status": t.status.value,
            "tags": t.tags or "",
            "is_recurring": t.is_recurring,
            "recurrence_type": t.recurrence_type.value if t.recurrence_type else None,
            "recurrence_interval": t.recurrence_interval,
            "recurrence_end_date": t.recurrence_end_date.isoformat() if t.recurrence_end_date else None
        }
    
    # REFLECTIONS — flat
    reflections = ReflectionNote.query.filter_by(user_id=user_id).all()
    def serialize_reflection(r):
        return {
            "note_type": r.note_type,
            "timeframe": r.timeframe,
            "date": r.date.isoformat(),
            "content": r.content or ""
        }
    
    # EVENTS — flat
    events = CalendarEvent.query.filter_by(user_id=user_id).all()
    def serialize_event(e):
        return {
            "title": e.title,
            "description": e.description or "",
            "start_datetime": e.start_datetime.isoformat(),
            "end_datetime": e.end_datetime.isoformat() if e.end_datetime else None,
            "all_day": e.all_day,
            "source": e.source,
            "uid": e.uid
        }
    
    return {
        "version": "1.0",
        "app": "wfm-power-planner",
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "warrior": username,
        "data": {
            "goals": [serialize_goal(g) for g in root_goals],
            "tasks": [serialize_task(t) for t in tasks],
            "reflection_notes": [serialize_reflection(r) for r in reflections],
            "calendar_events": [serialize_event(e) for e in events]
        }
    }

def wipe_all(user_id):
    """NUKE ENTIRE UNIVERSE — SAFE CASCADE"""
    # Goals — ORM cascade handles children
    Goal.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    # Tasks
    Task.query.filter_by(user_id=user_id).delete()
    # Reflections
    ReflectionNote.query.filter_by(user_id=user_id).delete()
    # Events
    CalendarEvent.query.filter_by(user_id=user_id).delete()
    db.session.commit()

def import_all(data_dict, user_id):
    """FULL RESTORE — rely on Flask's request transaction"""
    if data_dict.get("version") != "1.0":
        raise ValueError("Unsupported backup version")
    
    data = data_dict["data"]
    
    # NO with db.session.begin(): — let Flask route handle transaction
    wipe_all(user_id)
    
    # GOALS — recursive tree
    def import_goal(goal_dict, parent=None):
        new_goal = create_goal_from_dict(
            user_id=user_id,
            title=goal_dict["title"],
            description=goal_dict["description"],
            category=goal_dict["category"],
            status=goal_dict["status"],
            due_date=goal_dict["due_date"],
            is_habit=goal_dict["is_habit"],
            timeframe=goal_dict["timeframe"],
            parent=parent
        )
        for child in goal_dict.get("children", []):
            import_goal(child, new_goal)
        return new_goal
    
    for root in data.get("goals", []):
        import_goal(root)
    
    # TASKS
    for t in data.get("tasks", []):
        task = Task(
            user_id=user_id,
            title=t["title"],
            description=t["description"],
            due_date=t["due_date"],
            priority=TaskPriority[t["priority"].upper()],
            status=TaskStatus[t["status"].upper()],
            tags=t["tags"],
            is_recurring=t["is_recurring"],
            recurrence_type=TaskRecurrenceType[t["recurrence_type"].upper()] if t["recurrence_type"] else None,
            recurrence_interval=t["recurrence_interval"],
            recurrence_end_date=t["recurrence_end_date"]
        )
        db.session.add(task)
    
    # REFLECTIONS — upsert
    for r in data.get("reflection_notes", []):
        upsert_note(
            note_type=r["note_type"],
            timeframe=r["timeframe"],
            date_val=date.fromisoformat(r["date"]),
            content=r["content"]
        )
    
    # EVENTS — upsert by UID
    for e in data.get("calendar_events", []):
        print(f"Processing event: {e['title']} | UID: {e['uid']}")
        existing = CalendarEvent.query.filter_by(user_id=user_id, uid=e["uid"]).first()
        if existing:
            print(f"Updating existing event: {e['title']}")
            existing.title = e["title"]
            existing.description = e["description"]
            existing.start_datetime = datetime.fromisoformat(e["start_datetime"])
            existing.end_datetime = datetime.fromisoformat(e["end_datetime"]) if e["end_datetime"] else None
            existing.all_day = e["all_day"]
            existing.source = e["source"]
        else:
            event = CalendarEvent(
                user_id=user_id,
                uid=e["uid"],
                title=e["title"],
                description=e["description"],
                start_datetime=datetime.fromisoformat(e["start_datetime"]),
                end_datetime=datetime.fromisoformat(e["end_datetime"]) if e["end_datetime"] else None,
                all_day=e["all_day"],
                source=e["source"]
            )
            db.session.add(event)
            print(f"Created new event: {e['title']}")
    db.session.commit()
    # NO commit — Flask route will commit