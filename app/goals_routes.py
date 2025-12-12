# app/goals_routes.py
"""
GOALS API & VIEWS — TENET-COMPLIANT, CLEAN, ETERNAL
All goal-related routes live here — no clutter in __init__.py
"""

from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    abort,
    current_app
)
from flask_login import login_required, current_user
from datetime import datetime
import json

# MODELS
from app.models.goal import Goal, GoalStatus, GoalCategory, GoalTimeframe

# EXTENSIONS
from app.extensions import db

# SERVICES — ONE SOURCE OF TRUTH
from app.services.goal_service import (
    get_all_goals_tree,
    create_goal,
    create_goal_from_dict,
    move_goal,
    update_goal,
    delete_all_user_goals
)

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/goals')
@login_required
def goals_page():
    # Fetch root goals only — children are eager-loaded via relationship
    root_goals = Goal.query.filter_by(
        user_id=current_user.id,
        parent_id=None
    ).order_by(Goal.sort_order).all()

    return render_template(
        'goals.html',
        goals=root_goals,  # ONLY ROOT GOALS — CHILDREN COME VIA RELATIONSHIP
        goal_statuses=GoalStatus,
        goal_categories=GoalCategory,
        goal_timeframes=GoalTimeframe
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
        'is_habit': goal.is_habit,
        'timeframe': goal.timeframe.value
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
        status=data.get('status', 'todo'),
        parent_id=data.get('parent_id'),
        timeframe=data.get('timeframe', 'monthly')
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

# app/goals_routes.py
from app.services.goal_service import update_goal

@goals_bp.route('/api/goals/<int:goal_id>', methods=['PATCH'])
@login_required
def api_update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)

    data = request.get_json() or {}
    updated_goal = update_goal(goal_id, **data)
    return jsonify(goal_to_dict(updated_goal))

@goals_bp.route('/api/export')
@login_required
def export_data():
    """TENET #20 — FULL UNIVERSE EXPORT — SINGLE SOURCE OF TRUTH"""
    goals = get_all_goals_tree(current_user.id)
    
    # Convert to serializable format — ltree becomes string
    def serialize_goal(g):
        return {
            "id": g.id,
            "title": g.title,
            "description": g.description or "",
            "category": g.category.value,
            "status": g.status.value,
            "due_date": g.due_date.isoformat() if g.due_date else None,
            "is_habit": g.is_habit,
            "path": str(g.path),  # ltree → string
            "parent_id": g.parent_id,
            "progress": g.progress,
            "timeframe": g.timeframe.value,
            "children": [serialize_goal(c) for c in (g.children or [])]
        }

    export_data = {
        "exported_at": __import__('datetime').datetime.utcnow().isoformat() + "Z",
        "warrior": current_user.username,
        "goals": [serialize_goal(g) for g in goals if g.parent_id is None]
    }

    from datetime import datetime

    # ... inside export_data():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H%M')
    filename = f'wfm-power-planner-backup_{timestamp}.json'

    return (
        jsonify(export_data),
        200,
        {
            'Content-Type': 'application/json',
            'Content-Disposition': f'attachment; filename={filename}'
        }
)


@goals_bp.route('/api/import', methods=['POST'])
@login_required
def import_data():
    """TENET #20 — FULL UNIVERSE RESTORE — TOTAL DOMINATION"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({"error": "Only JSON backups allowed"}), 400

    try:
        data = json.load(file)
        goals_data = data.get("goals", [])

        # NUCLEAR OPTION — WIPE CURRENT UNIVERSE
        delete_all_user_goals(current_user.id)

        # Rebuild tree using new IDs — ltree path is rebuilt correctly
        def import_goal(goal_dict, parent=None):
            new_goal = create_goal_from_dict(
                user_id=current_user.id,
                title=goal_dict["title"],
                description=goal_dict["description"],
                category=goal_dict["category"],
                status=goal_dict["status"],
                due_date=goal_dict["due_date"],
                is_habit=goal_dict["is_habit"],
                parent=parent,
                timeframe=goal_dict.get("timeframe", "monthly")
            )
            # Children will use new_goal.id in their path — handled in service
            for child in goal_dict.get("children", []):
                import_goal(child, new_goal)
            return new_goal

        for root in goals_data:
            import_goal(root)

        return jsonify({"message": "Empire restored. Hulkamania runs wild again."}), 200

    except Exception as e:
        current_app.logger.error(f"Import failed: {e}")
        return jsonify({"error": "Backup corrupted or incompatible"}), 500