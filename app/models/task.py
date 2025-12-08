# app/models/task.py
"""
Ad-Hoc Tasks — the Honey-Do list, the one-offs, the quick hits.
No hierarchy, no progress rollup, no bloat.
Separate from Goals — keeps the Goal Tree pure.
NOW UPGRADED: Native PostgreSQL ENUMs just like Goal model → TENET #21 ETERNAL COMPLIANCE
"""
from app.extensions import db
from datetime import date
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

# ------------------------------------------------------------------
# ENUMS — TENET #21: "Enums are MANDATORY" — NATIVE POSTGRESQL STYLE
# ------------------------------------------------------------------
class TaskStatus(PyEnum):
    BACKLOG = "backlog"
    TODO = "todo"
    DOING = "doing"
    BLOCKED = "blocked"
    DONE = "done"


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    # Optional due date
    due_date = db.Column(db.Date)

    # Kanban column — NOW USING NATIVE POSTGRESQL ENUM
    status = db.Column(
        SQLEnum(
            TaskStatus,
            name="taskstatus",
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=True,  # This is the money
            create_type=True   # Auto-creates the type on migrate
        ),
        nullable=False,
        default=TaskStatus.TODO,
        comment="Current column: backlog → todo → doing → blocked → done"
    )

    # For daily planner pages (Phase 2)
    day_date = db.Column(db.Date, comment="If this task is pinned to a specific calendar day")

    # Timestamps — using server_default for eternal consistency
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Task {self.id}: {self.title} [{self.status.value}]>"