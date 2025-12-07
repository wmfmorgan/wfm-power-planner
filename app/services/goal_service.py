# app/services/goal_service.py
"""
GOAL SERVICE — SINGLE SOURCE OF TRUTH FOR ALL GOAL WRITES
Tenet #17 — ALL DB writes go through service layer
No route touches db.session directly ever again
"""

from app.extensions import db
from app.models.goal import Goal, GoalStatus, GoalCategory
from sqlalchemy_utils.types.ltree import Ltree

def create_goal(user_id: int, title: str, category: str, status: str = "todo", parent_id: int | None = None) -> Goal:
    goal = Goal(
        user_id=user_id,
        title=title,
        category=GoalCategory[category.upper()],
        status=GoalStatus[status.upper()],
        path=Ltree('root') if parent_id is None else _get_child_path(parent_id)
    )
    db.session.add(goal)
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