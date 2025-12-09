# app/services/goal_service.py
"""
GOAL SERVICE — SINGLE SOURCE OF TRUTH FOR ALL GOAL WRITES
Tenet #17 — ALL DB writes go through service layer
No route touches db.session directly ever again
"""

from app.extensions import db
from app.models.goal import Goal, GoalStatus, GoalCategory
from sqlalchemy_utils.types.ltree import Ltree

def create_goal(
    user_id: int,
    title: str,
    description: str = "",
    category: str = "work",        # ← DEFAULT ADDED
    due_date: str | None = None,
    is_habit: bool = False,
    status: str = "todo",
    parent_id: int | None = None
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
    if parent_id is None:
        path = Ltree('root')
    else:
        parent = Goal.query.get_or_404(parent_id)
        path = parent.path + Ltree(str(parent.id))

    goal = Goal(
        user_id=user_id,
        title=title.strip(),
        description=description.strip() if description else None,
        category=GoalCategory[category.upper()],  # still safe
        status=GoalStatus[status.upper()],
        due_date=due_date_obj,
        is_habit=is_habit,
        parent_id=parent_id,
        path=path
    )
    db.session.add(goal)
    db.session.commit()
    
    # Refresh to get updated path with new ID
    db.session.refresh(goal)
    
    # If has parent, update path to include self (ltree requires final ID)
    if parent_id is not None:
        goal.path = path + Ltree(str(goal.id))
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

    allowed_fields = {'title', 'description', 'status', 'category', 'due_date', 'is_habit'}
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
        else:
            setattr(goal, field, value or None)

    db.session.commit()
    return goal