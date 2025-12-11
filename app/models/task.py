# app/models/task.py — PHASE 3.1 TASKS ENGINE — TENET-COMPLIANT ETERNAL DOMINATION
from app.extensions import db
from datetime import date
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    DOING = "doing"
    BLOCKED = "blocked"
    DONE = "done"

class TaskRecurrenceType(Enum):
    DAILY   = "daily"
    WEEKLY  = "weekly"
    MONTHLY = "monthly"

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    
    # PHASE 3.1 CORE FIELDS
    due_date = db.Column(db.Date)                    # Optional due date

    priority = db.Column(SQLEnum(
        TaskPriority, 
        name="taskpriority", 
        values_callable=lambda enum: [e.value for e in enum],
        native_enum=True,
        ),
        nullable=False,
        default=TaskPriority.MEDIUM
    )
    
    tags = db.Column(db.Text, default="")             # Comma-separated, e.g. "work,urgent"

    # Kanban column
    status = db.Column(SQLEnum(
        TaskStatus, 
        name="taskstatus", 
        values_callable=lambda enum: [e.value for e in enum],
        native_enum=True,
        ),
        nullable=False,
        default=TaskStatus.BACKLOG
    )
    # Manual ordering within same status (for future Kanban reordering)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    # Optional tie to a specific calendar day (for day view)
    day_date = db.Column(db.Date)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    # === PHASE 3.2 RECURRING TASKS ===
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    recurrence_type = db.Column(SQLEnum(
        TaskRecurrenceType, 
        name='taskrecurrencetype',
        values_callable=lambda enum: [e.value for e in enum],
        native_enum=True,
        ),
        nullable=True,
        default=TaskRecurrenceType.DAILY
    )
    recurrence_interval = db.Column(db.Integer, default=1)  # every 1 day/week/month
    recurrence_end_date = db.Column(db.Date, nullable=True) # optional end date

    # Track the original recurring task (for instances)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    is_instance = db.Column(db.Boolean, nullable=False, default=False)  # true = spawned instance
    original_due_date = db.Column(db.Date, nullable=True)  # for monthly "day 15" logic

    # === PHASE 3.3 — HABIT STREAKS & FIRE ===
    is_habit = db.Column(db.Boolean, nullable=False, default=False)
    current_streak = db.Column(db.Integer, nullable=False, default=0)
    longest_streak = db.Column(db.Integer, nullable=False, default=0)
    last_completed_date = db.Column(db.Date, nullable=True)
    total_completions = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return (f"<Task {self.id}: {self.title} | "
                f"Recur: {self.is_recurring} {self.recurrence_type} every {self.recurrence_interval} | "
                f"Status: {self.status.value}>")