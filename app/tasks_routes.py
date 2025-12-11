# app/tasks_routes.py — PHASE 3.1 TASKS ENGINE — FULL CRUD
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from app.services.task_service import get_all_tasks, create_task, update_task, delete_task

tasks_bp = Blueprint('tasks', __name__, template_folder='templates/tasks')

@tasks_bp.route('/tasks')
@login_required
def tasks_page():
    return render_template('tasks.html')

@tasks_bp.route('/api/tasks')
@login_required
def api_tasks():
    tasks = get_all_tasks()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description or '',
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'priority': t.priority.value,
        'tags': t.tags,
        'status': t.status.value,
        'day_date': t.day_date.isoformat() if t.day_date else None
    } for t in tasks])

@tasks_bp.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.get_json()
    task = create_task(
        title=data['title'],
        description=data.get('description', ''),
        due_date=data.get('due_date'),
        priority=data.get('priority', 'medium'),
        tags=data.get('tags', ''),
        status=data.get('status', 'backlog'),
        day_date=data.get('day_date')
    )
    return jsonify({'id': task.id, 'message': 'Task forged!'}), 201

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