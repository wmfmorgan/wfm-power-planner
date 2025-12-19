# app/services/task_service.py — TENET #17 OBEYED — ALL WRITES THROUGH SERVICE LAYER
from app.extensions import db
from app.models.task import Task, TaskPriority, TaskStatus, TaskRecurrenceType
from flask_login import current_user
from datetime import date, timedelta

def get_all_tasks():
    return Task.query.filter_by(user_id=current_user.id).order_by(Task.sort_order, Task.id).all()

def create_task(title, description="", due_date=None, priority="medium", tags="", status="backlog",
                is_recurring=False, recurrence_type=None, recurrence_interval=1, recurrence_end_date=None,
                from_day_page=False):

    if from_day_page and not due_date:
        due_date = date.today()

    task = Task(
        user_id=current_user.id,
        title=title.strip(),
        description=description.strip() if description else None,
        due_date=due_date,                               # ← now auto-set here too (double safety)
        priority=TaskPriority[priority.upper()].value if priority else TaskPriority.MEDIUM.value,
        tags=tags.strip() if tags else None,
        status=TaskStatus.TODO.value if from_day_page else (TaskStatus[status.upper()].value if status else TaskStatus.BACKLOG.value),
        is_recurring=is_recurring,
        recurrence_type=TaskRecurrenceType[recurrence_type.upper()].value if recurrence_type else None,
        recurrence_interval=recurrence_interval,
        recurrence_end_date=recurrence_end_date,
        sort_order=0
    )
    db.session.add(task)
    db.session.commit()
    return task

def update_task(task_id, **updates):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        raise PermissionError("Not your task, brother!")

    allowed = {
        'title', 'description', 'due_date', 'priority', 'tags', 'status',
        'is_recurring', 'recurrence_type', 'recurrence_interval', 'recurrence_end_date'
    }

    for key, value in updates.items():
        if key not in allowed:
            continue

        if key == 'priority':
            task.priority = TaskPriority[value.upper()].value
        elif key == 'status':
            task.status = TaskStatus[value.upper()].value
        elif key == 'recurrence_type':  # ← THIS IS THE MONEY LINE
            task.recurrence_type = TaskRecurrenceType[value.upper()].value if value else None
        elif key == 'due_date' or key == 'recurrence_end_date' or key == 'day_date':
            setattr(task, key, value or None)
        else:
            setattr(task, key, value)

    db.session.commit()
    return task

def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        raise PermissionError("Not your task!")
    db.session.delete(task)
    db.session.commit()

def create_recurring_task(**kwargs):
    """Create a recurring master task — no instances yet"""
    kwargs['is_recurring'] = True
    return create_task(**kwargs)

def spawn_recurring_instances_for_date(target_date: date):
    """Called daily by background job or on /today load"""
    recurring = Task.query.filter(
        Task.is_recurring == True,
        Task.recurrence_end_date.is_(None) | (Task.recurrence_end_date >= target_date)
    ).all()

    for master in recurring:
        # Skip if instance already exists for this date
        exists = Task.query.filter_by(
            parent_task_id=master.id,
            due_date=target_date,
            is_instance=True
        ).first()
        if exists:
            continue

        # Calculate next due date based on recurrence_type
        next_due = calculate_next_due(master, target_date)
        if next_due != target_date:
            continue

        # SPAWN THE INSTANCE
        instance = Task(
            user_id=master.user_id,
            title=master.title,
            description=master.description,
            due_date=target_date,
            priority=master.priority,
            tags=master.tags,
            status='todo',
            is_recurring=False,
            is_instance=True,
            parent_task_id=master.id,
            original_due_date=master.due_date
        )
        db.session.add(instance)
    db.session.commit()

def calculate_next_due(master: Task, from_date: date) -> date:
    if not master.is_recurring:
        return from_date

    if master.recurrence_type == 'daily':
        delta = timedelta(days=master.recurrence_interval)
        days_since_start = (from_date - master.due_date).days
        intervals_passed = days_since_start // master.recurrence_interval
        return master.due_date + (intervals_passed + 1) * delta

    if master.recurrence_type == 'weekly':
        delta = timedelta(weeks=master.recurrence_interval)
        weeks_since_start = (from_date - master.due_date).days // 7
        intervals_passed = weeks_since_start // master.recurrence_interval
        return master.due_date + (intervals_passed + 1) * delta

    if master.recurrence_type == 'monthly':
        # "Every 2nd Tuesday" logic coming in next drop — this handles basic monthly for now
        year = from_date.year
        month = from_date.month + master.recurrence_interval
        while month > 12:
            month -= 12
            year += 1
        # Simple day-of-month match (handles Feb 30 → rolls to March)
        try:
            return date(year, month, master.due_date.day)
        except ValueError:
            # Last day of month if original day doesn't exist
            from calendar import monthrange
            return date(year, month, monthrange(year, month)[1])

    return from_date  # fallback

def get_tasks_for_day(target_date: date):
    """Get all tasks due on a specific day — TENET #17 OBEYED"""
    return Task.query.filter(
        Task.user_id == current_user.id,
        db.func.date(Task.due_date) == target_date
    ).order_by(Task.sort_order).all()

def move_task(task_id: int, new_status: str):
    """Move task to new status — THROUGH SERVICE LAYER ONLY"""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        raise PermissionError("Not your task, brother!")
    task.status = TaskStatus[new_status.upper()].value
    db.session.commit()
    return task

def delete_all_user_tasks(user_id): 
    Task.query.filter_by(user_id=user_id).delete()
    db.session.commit()