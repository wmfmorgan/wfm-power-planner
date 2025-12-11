# app/services/task_service.py — TENET #17 OBEYED — ALL WRITES THROUGH SERVICE LAYER
from app.extensions import db
from app.models.task import Task, TaskPriority, TaskStatus
from flask_login import current_user
from datetime import date

def get_all_tasks():
    return Task.query.filter_by(user_id=current_user.id).order_by(Task.sort_order, Task.id).all()

def create_task(title, description="", due_date=None, priority="medium", tags="", status="backlog", day_date=None):
    
    task = Task(
        user_id=current_user.id,
        title=title.strip(),
        description=description.strip() or None,
        due_date=due_date,
        priority=TaskPriority[priority.upper()].value,
        tags=tags.strip(),
        status=TaskStatus[status.upper()].value,
        day_date=day_date
    )
    
    db.session.add(task)
    db.session.commit()
    return task

def update_task(task_id, **updates):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        raise PermissionError("Not your task, brother!")

    allowed = {'title', 'description', 'due_date', 'priority', 'tags', 'status', 'day_date'}
    for key, value in updates.items():
        if key in allowed:
            if key == 'priority':
                setattr(task, key, TaskPriority[value.upper()].value)
            elif key == 'status':
                setattr(task, key, TaskStatus[value.upper()].value)
            elif key == 'due_date' or key == 'day_date':
                setattr(task, key, value or None)
            else:
                setattr(task, key, value.strip() if value else None)
    db.session.commit()
    return task

def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        raise PermissionError("Not your task!")
    db.session.delete(task)
    db.session.commit()