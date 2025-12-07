# app/goals_routes.py
"""
GOALS API & VIEWS — TENET-COMPLIANT, CLEAN, ETERNAL
All goal-related routes live here — no clutter in __init__.py
"""

from app.models.goal import Goal, GoalCategory, GoalStatus
from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from sqlalchemy_utils import LtreeType
from sqlalchemy_utils.types.ltree import Ltree
from app.services.goal_service import create_goal, move_goal

goals_bp = Blueprint('goals', __name__)

# HTML: Kanban + Tree page
@goals_bp.route('/goals')
@login_required
def goals_page():
    return render_template('goals.html')

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
        'category': goal.category.value,
        'status': goal.status.value,
        'progress': goal.progress or 0
    }

@goals_bp.route('/api/goals', methods=['POST'])
@login_required
def api_create_goal():
    data = request.get_json()
    goal = create_goal(
        user_id=current_user.id,
        title=data['title'],
        category=data['category']
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