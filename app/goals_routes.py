# app/goals_routes.py
"""
GOALS API & VIEWS — TENET-COMPLIANT, CLEAN, ETERNAL
All goal-related routes live here — no clutter in __init__.py
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.goal import Goal

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