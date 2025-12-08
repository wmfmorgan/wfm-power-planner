# app/goals_routes.py
"""
GOALS API & VIEWS — TENET-COMPLIANT, CLEAN, ETERNAL
All goal-related routes live here — no clutter in __init__.py
"""

from app.models.goal import Goal, GoalStatus, GoalCategory
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.services.goal_service import create_goal, move_goal

goals_bp = Blueprint('goals', __name__)

# HTML: Kanban + Tree page
@goals_bp.route('/goals')
@login_required
def goals_page():
    return render_template(
        'goals.html',
        goal_statuses=GoalStatus,           # pass the enum itself
        goal_categories=GoalCategory,        # pass the enum itself
        # NO MORE status_display OR category_display DICTIONARIES
        # WE LET JINJA + ENUM DO THE WORK
    )

# API: Full goal tree as JSON
@goals_bp.route('/api/goals')
@login_required
def api_goals():
    
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    # Build proper nested tree
    goal_map = {goal.id: goal_to_dict(goal) for goal in goals}
    
    for goal in goals:
        if goal.parent_id and goal.parent_id in goal_map:
            parent = goal_map[goal.parent_id]
            parent.setdefault('children', []).append(goal_map[goal.id])
    
    tree = [goal_map[goal.id] for goal in goals if goal.parent_id is None]
    return jsonify(tree)

def goal_to_dict(goal):
    return {
        'id': goal.id,
        'title': goal.title,
        'description': goal.description or '',
        'category': goal.category.value,
        'status': goal.status.value,
        'progress': goal.progress or 0,
        'due_date': goal.due_date.isoformat() if goal.due_date else None,
        'is_habit': goal.is_habit
    }

@goals_bp.route('/api/goals', methods=['POST'])
@login_required
def api_create_goal():
    data = request.get_json()
    
    goal = create_goal(
        user_id=current_user.id,
        title=data['title'],
        description=data.get('description', ''),
        category=data['category'],
        due_date=data.get('due_date'),
        is_habit=data.get('is_habit', False),
        status=data.get('status', 'todo')  # optional override
    )
    
    return jsonify(goal_to_dict(goal))

@goals_bp.route('/api/goals/<int:goal_id>/move', methods=['POST'])
@login_required
def api_move_goal(goal_id):
    data = request.get_json()
    goal = move_goal(
        goal_id=goal_id,
        new_status=data['status'],
        new_parent_id=data.get('parent_id')  # optional for future hierarchy moves
    )
    return jsonify(goal_to_dict(goal))