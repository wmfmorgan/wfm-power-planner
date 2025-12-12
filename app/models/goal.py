# app/models/goal.py
"""
The beating heart of WFM-POWER-PLANNER.

This is the Goal model — hierarchical, Kanban-powered, and built on PostgreSQL ltree.
Every goal can have children → sub-goals → steps → tasks.
Every goal lives in one of five sacred columns.
Every goal belongs to one of eight sacred life categories.

Tenet #15: Championship-level comments — fulfilled.
Tenet #16: Recursive hierarchy via ltree — fulfilled.
Tenet #21: Enums mandatory — fulfilled.
Tenet #31: Using official Flask extensions — fulfilled.

This model will dominate 2025 and beyond.
"""

from sqlalchemy_utils import LtreeType
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from datetime import datetime
from app.extensions import db

# ------------------------------------------------------------------
# ENUMS — TENET #21: "Enums are MANDATORY"
# ------------------------------------------------------------------
class GoalStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    DOING = "doing"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"

class GoalCategory(Enum):
    MARITAL = "marital"
    SOCIAL = "social"
    FINANCIAL = "financial"
    WORK = "work"
    FAMILY = "family"
    SPIRITUAL = "spiritual"
    HEALTH = "health"
    HOBBY = "hobby"

class GoalTimeframe(Enum):
    YEARLY    = "yearly"
    QUARTERLY = "quarterly"
    MONTHLY   = "monthly"
    WEEKLY    = "weekly"
    DAILY     = "daily"
# ------------------------------------------------------------------
# GOAL MODEL — THE GOAL THAT NEVER TAPS OUT
# ------------------------------------------------------------------
class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True,
                       comment="Owner of the goal — Single Warrior Mode")
    
    title = db.Column(db.Text, nullable=False, comment="The name of the goal — e.g., 'Run a marathon'")
    description = db.Column(db.Text, comment="Why this goal matters — the fire behind it")
    
    # Sacred category — color-coded in UI
    category = db.Column(SQLEnum(
        GoalCategory,
        name="goalcategory",
        values_callable=lambda enum: [e.value for e in enum],
        native_enum=True,  # keep using PostgreSQL enum type
        ), 
        nullable=False, default=GoalCategory.WORK,
        comment="One of the 8 life domains")
    
    timeframe = db.Column(SQLEnum(
        GoalTimeframe, 
        name="goaltimeframe",
        values_callable=lambda enum: [e.value for e in enum], 
        native_enum=True,
        ), nullable=False,
        default=GoalTimeframe.MONTHLY,
        comment="Planning horizon: yearly → quarterly → monthly → weekly → daily"
        )

    # Optional due date — inherited by children
    due_date = db.Column(db.Date, nullable=True, comment="When this goal should be complete")
    
    # Habit goals repeat daily/weekly — Phase 4
    is_habit = db.Column(db.Boolean, nullable=False, default=False,
                        comment="True = auto-create daily instances (Phase 4)")
    
    # When status → DONE
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=True)
    path = db.Column(LtreeType, nullable=False, index=True,
                     comment="Materialized path: 1.3.2 — enables O(1) subtree queries")
    
    # Kanban column
    status = db.Column(SQLEnum(
        GoalStatus,
        name="goalstatus",
        values_callable=lambda enum: [e.value for e in enum],
        native_enum=True,
        ), nullable=False, default=GoalStatus.TODO,
                      comment="Current column: backlog → todo → doing → blocked → done")
    
    # Manual ordering within same parent
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = db.relationship(
        'Goal',
        backref=db.backref('parent', remote_side=[id]),
        lazy='joined',          # EAGER LOAD CHILDREN
        order_by="Goal.sort_order",
        cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Goal {self.id}: {self.title} [{self.status.value}]>"

    # ------------------------------------------------------------------
    # Helper: Get all descendants (sub-goals) — used for progress rollup
    # ------------------------------------------------------------------
    def get_descendants(self):
        from sqlalchemy import text
        query = text("SELECT id FROM goals WHERE path <@ :path AND id != :id")
        result = db.session.execute(query, {"path": str(self.path), "id": self.id})
        return [row[0] for row in result]

    # ------------------------------------------------------------------
    # Helper: Progress % — leaf-node count only (Phase 1)
    # ------------------------------------------------------------------
    @property
    def progress(self):
        descendants = self.get_descendants()
        if not descendants:
            return 100 if self.status == GoalStatus.DONE else 0
        
        completed = Goal.query.filter(
            Goal.id.in_(descendants),
            Goal.status == GoalStatus.DONE
        ).count()
        total = len(descendants)
        return round((completed / total) * 100, 1) if total else 0