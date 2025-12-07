# app/goals_routes.py
"""
GOALS API & VIEWS — TENET-COMPLIANT, CLEAN, ETERNAL
All goal-related routes live here — no clutter in __init__.py
"""

from app.models.goal import Goal, GoalCategory, GoalStatus
from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.goal import Goal
from sqlalchemy_utils import LtreeType
from sqlalchemy_utils.types.ltree import Ltree

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
    
    def build_node(goal):
        node = {
            'id': goal.id,
            'title': goal.title,
            'category': goal.category.value,
            'status': goal.status.value,
            'progress': goal.progress
        }
        children = [build_node(g) for g in goals if g.parent_id == goal.id]
        if children:
            node['children'] = children
        return node
    
    tree = [build_node(g) for g in goals if g.parent_id is None]
    return jsonify(tree)

def goal_to_dict(goal):
    return {
        'id': goal.id,
        'title': goal.title,
        'category': goal.category.value,
        'status': goal.status.value,
        'progress': goal.progress
    }

@goals_bp.route('/api/goals', methods=['POST'])
@login_required
def create_goal():
    data = request.get_json()
    goal = Goal(
        user_id=current_user.id,
        title=data['title'],
        category=GoalCategory[data['category']],
        status=GoalStatus.TODO,
        path=Ltree('root')
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify(goal_to_dict(goal))

@goals_bp.route('/api/goals/<int:goal_id>/move', methods=['POST'])
@login_required
def move_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)
    data = request.get_json()
    goal.status = GoalStatus[data['status']]
    db.session.commit()
    return jsonify({'success': True})