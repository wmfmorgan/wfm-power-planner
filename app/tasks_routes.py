# app/tasks_routes.py — PHASE 3.1 TASKS ENGINE — FULL CRUD
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from app.services.task_service import get_all_tasks, create_task, update_task, delete_task, get_tasks_for_day, move_task
from app.models.task import Task, TaskPriority, TaskStatus, TaskRecurrenceType
from datetime import date
from app.extensions import db

def task_to_dict(task):
    """Convert Task model to JSON-serializable dict — PURE CHAMPIONSHIP FORMAT"""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description or '',
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'priority': task.priority.value,           # ← "low", "critical", etc.
        'tags': task.tags,
        'status': task.status.value,               # ← "backlog", "todo", etc.
        'is_recurring': task.is_recurring,
        'recurrence_type': task.recurrence_type.value if task.recurrence_type else None,
        'recurrence_interval': task.recurrence_interval,
        'recurrence_end_date': task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
        'is_instance': task.is_instance,
        'parent_task_id': task.parent_task_id,
        'original_due_date': task.original_due_date.isoformat() if task.original_due_date else None,
        'sort_order': task.sort_order,
        'day_date': task.day_date.isoformat() if task.day_date else None,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat()
    }

tasks_bp = Blueprint('tasks', __name__, template_folder='templates/tasks')

@tasks_bp.route('/tasks')
@login_required
def tasks_page():
    # PHASE 3.1 — TASKS ENGINE — TENET-COMPLIANT RENDERING
    # Exactly like goals_page() — no shortcuts, no weakness
    tasks = Task.query.filter_by(user_id=current_user.id)\
                      .order_by(Task.sort_order, Task.id)\
                      .all()

    return render_template(
        'tasks.html',
        tasks=tasks,
        task_statuses=TaskStatus,
        task_priorities=TaskPriority,
        task_recurrence_types=TaskRecurrenceType,
        kanban_id='tasks-kanban',
        kanban_statuses=TaskStatus,
        kanban_type='task'
    )

@tasks_bp.route('/api/tasks')
@login_required
def api_tasks():
    tasks = get_all_tasks()
    return jsonify([task_to_dict(t) for t in tasks])

@tasks_bp.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.get_json() or {}

    print("=== TASK CREATE DEBUG ===")
    print("Raw JSON from frontend:", data)
    print("is_recurring:", data.get('is_recurring'))
    print("recurrence_type:", data.get('recurrence_type'))
    print("recurrence_interval:", data.get('recurrence_interval'))
    print("recurrence_end_date:", data.get('recurrence_end_date'))
    print("=========================")

    task = create_task(
        title=data.get('title', ''),
        description=data.get('description', ''),
        due_date=data.get('due_date'),
        priority=data.get('priority', 'medium'),
        tags=data.get('tags', ''),
        status=data.get('status', 'backlog'),
        is_recurring=data.get('is_recurring', False),
        recurrence_type=data.get('recurrence_type'),
        recurrence_interval=data.get('recurrence_interval', 1),
        recurrence_end_date=data.get('recurrence_end_date')
    )
    return jsonify(task_to_dict(task)), 201

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PATCH'])
@login_required
def api_update_task(task_id):
    data = request.get_json() or {}
    task = update_task(task_id, **data)
    return jsonify({'message': 'Task updated!'})

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    delete_task(task_id)
    return jsonify({'message': 'Task obliterated!'})

@tasks_bp.route('/api/tasks/<int:task_id>')
@login_required
def api_get_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    return jsonify(task_to_dict(task))

@tasks_bp.route('/api/tasks/period/day/<int:year>/<int:month>/<int:day>')
@login_required
def api_tasks_day(year, month, day):
    target_date = date(year, month, day)
    tasks = get_tasks_for_day(target_date)  # ← SERVICE LAYER
    return jsonify([task_to_dict(t) for t in tasks])

@tasks_bp.route('/api/tasks/<int:task_id>/move', methods=['POST'])
@login_required
def api_move_task(task_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "status required"}), 400

    task = move_task(task_id, new_status)  # ← SERVICE LAYER
    return jsonify(task_to_dict(task))