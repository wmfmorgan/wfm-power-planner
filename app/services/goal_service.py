# app/services/goal_service.py
"""
GOAL SERVICE — SINGLE SOURCE OF TRUTH FOR ALL GOAL WRITES
Tenet #17 — ALL DB writes go through service layer
No route touches db.session directly ever again
"""

from app.extensions import db
from app.models.goal import Goal, GoalStatus, GoalCategory, GoalTimeframe
from sqlalchemy_utils.types.ltree import Ltree
from flask_login import current_user
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from ..models.goal import Goal
from ..extensions import db
from flask import jsonify

import logging

def get_all_goals_tree(user_id):
    """
    TENET #20 — Return complete goal tree with children eager-loaded
    Used by export and potentially future features
    """
    return (
        Goal.query
        .options(joinedload(Goal.children))
        .filter_by(user_id=user_id, parent_id=None)
        .order_by(Goal.sort_order)
        .all()
    )

def create_goal(
    user_id: int,
    title: str,
    description: str = "",
    category: str = "work",        
    due_date: str | None = None,
    is_habit: bool = False,
    status: str = "todo",
    parent_id: int | None = None,
    timeframe: str | None = None
    ) -> Goal:
    """
    FORGE A NEW GOAL — FULLY WEAPONIZED FOR 2025 DOMINATION
    Tenet #17: All DB writes go through service layer — OBEYED
    """
    from datetime import datetime

    # Convert due_date string (YYYY-MM-DD) → date object
    due_date_obj = None
    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid due date format — must be YYYY-MM-DD")

    # Determine ltree path
    # Determine initial path — temp to satisfy NOT NULL
    path = Ltree('temp')  # dummy — will be overwritten

    if parent_id is not None:
        parent = Goal.query.get_or_404(parent_id)
        # Depth check
        depth = 0
        current = parent
        while current.parent_id:
            depth += 1
            current = Goal.query.get(current.parent_id)
        if depth >= 4:
            raise ValueError("Maximum goal depth of 5 levels reached")
    else:
        parent = None  # for later use

    # Validate category
    try:
        category_enum = GoalCategory[category.upper()]
    except KeyError:
        raise ValueError(f"Invalid category: {category}")

    # Validate status
    try:
        status_enum = GoalStatus[status.upper()]
    except KeyError:
        raise ValueError(f"Invalid status: {status}")

    # Validate timeframe if provided
    if timeframe:
        try:
            timeframe_enum = GoalTimeframe[timeframe.upper()]
        except KeyError:
            raise ValueError(f"Invalid timeframe: {timeframe}")
    else:
        # TIMEFRAME INHERITANCE
        timeframe_to_use = timeframe or 'monthly'
        if parent_id and timeframe is None:
            inheritance_map = {
                'yearly': 'quarterly',
                'quarterly': 'monthly',
                'monthly': 'weekly',
                'weekly': 'daily',
                'daily': 'daily'
            }
            timeframe_to_use = inheritance_map.get(parent.timeframe.value, 'monthly')
        timeframe_enum = GoalTimeframe[timeframe_to_use.upper()]

    goal = Goal(
        user_id=user_id,
        title=title.strip(),
        description=description.strip() if description else None,
        category=GoalCategory[category.upper()],
        status=GoalStatus[status.upper()],
        due_date=due_date_obj,
        is_habit=is_habit,
        parent_id=parent_id,
        timeframe=timeframe_enum,
        path=path  # temp path
    )

    db.session.add(goal)
    db.session.flush()  # get ID

    # NOW BUILD CORRECT PATH
    if parent:
        goal.path = parent.path + Ltree(str(goal.id))
    else:
        goal.path = Ltree(str(goal.id))

    db.session.commit()
    return goal

def move_goal(goal_id: int, new_status: str, new_parent_id: int | None = None):
    goal = Goal.query.get_or_404(goal_id)
    goal.status = GoalStatus[new_status.upper()]
    
    if new_parent_id is not None:
        goal.path = _get_child_path(new_parent_id)
    
    db.session.commit()
    return goal

def _get_child_path(parent_id: int) -> Ltree:
    parent = Goal.query.get_or_404(parent_id)
    return Ltree(str(parent.path) + '.' + str(parent.id))

# app/services/goal_service.py
def update_goal(goal_id: int, **updates) -> Goal:
    """
    UPDATE A GOAL — TENET #17 OBEYED ETERNALLY
    Only place that touches Goal model for writes.
    """
    goal = Goal.query.get_or_404(goal_id)

    # CYCLE DETECTION FOR PARENT CHANGE
    new_parent_id = updates.get('parent_id')
    if new_parent_id is not None and new_parent_id != goal.parent_id:
        if new_parent_id == goal_id:
            raise ValueError("Goal cannot be its own parent")
        
        # Walk up from new parent — if we hit goal_id, cycle!
        current = Goal.query.get(new_parent_id)
        seen = set()
        while current:
            if current.id == goal_id:
                raise ValueError("Cycle detected in goal hierarchy")
            if current.id in seen:
                break  # safety
            seen.add(current.id)
            current = current.parent

    allowed_fields = {'title', 'description', 'status', 'category', 'due_date', 'is_habit', 'timeframe'}
    for field, value in updates.items():
        if field not in allowed_fields:
            continue

        if field == 'status':
            goal.status = GoalStatus[value.upper()]
        elif field == 'category':
            goal.category = GoalCategory[value.upper()]
        elif field == 'due_date':
            goal.due_date = value or None
        elif field == 'is_habit':
            goal.is_habit = bool(value)
        elif field == 'timeframe':
            goal.timeframe = GoalTimeframe[value.upper()]
        else:
            setattr(goal, field, value or None)

    if 'parent_id' in updates:
        goal.parent_id = updates['parent_id']

    db.session.commit()
    return goal

# services/goal_service.py

def delete_all_user_goals(user_id):
    """NUCLEAR OPTION — USED BEFORE IMPORT"""
    db.session.execute(
        text("DELETE FROM goals WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    db.session.commit()

def create_goal_from_dict(**kwargs):
    """Used by import — builds path correctly using new ID"""
    user_id = kwargs.pop("user_id")
    parent = kwargs.pop("parent", None)

    goal = Goal(user_id=user_id, **kwargs)
    db.session.add(goal)
    db.session.flush()  # Gets new ID

    # Rebuild path using new reality
    if parent:
        goal.path = parent.path + Ltree(str(goal.id))
    else:
        goal.path = Ltree(str(goal.id))

    db.session.commit()
    return goal

def delete_goal(goal_id: int) -> None:
    """
    TOTAL SUBTREE ANNIHILATION — TENET #17 OBEYED
    Deletes a goal AND ALL ITS DESCENDANTS forever.
    PostgreSQL + SQLAlchemy cascade="all, delete-orphan" + ON DELETE CASCADE 
    does the heavy lifting — zero manual recursion needed.
    Fast. Clean. Unbreakable.
    """
    goal = Goal.query.get_or_404(goal_id)
    db.session.delete(goal)  # CASCADE NUKES EVERY CHILD
    db.session.commit()

__all__ = [
    'create_goal',
    'move_goal',
    'update_goal',
    'delete_all_user_goals',
    'create_goal_from_dict',
    'get_all_goals_tree',   # ← THIS MUST BE HERE
]

