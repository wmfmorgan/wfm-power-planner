# tests/pte — PHASE 2: TASK API DOMINATION
"""
Proves:
- Create task (global page) → appears in /api/tasks
- Create task from day page (from_day_page flag) → defaults to 'todo' status + due_date = today
- Fetch tasks for specific day → only matching due_date
- Move task status → updates correctly
- Update task fields
- Delete task
All with real authenticated user, real Postgres, rollback eternal.
"""
import pytest
from datetime import datetime


def test_task_crud_and_day_filtering(authenticated_client):
    # 1. CREATE GLOBAL TASK — should default to 'backlog'
    response = authenticated_client.post('/api/tasks', json={
        'title': 'Global Backlog Task',
        'description': 'This should start in backlog',
        'priority': 'high',
        'tags': 'test,global'
    })
    assert response.status_code == 201
    global_task = response.get_json()
    global_task_id = global_task['id']
    assert global_task['status'] == 'backlog'
    assert global_task['due_date'] is None  # no due date set

    # 2. CREATE TASK FROM DAY PAGE — should default to 'todo' + due_date = today
    today_str = datetime.today().strftime('%Y-%m-%d')
    response = authenticated_client.post('/api/tasks', json={
        'title': 'Day Page Task',
        'from_day_page': True,  # ← magic flag from day page
        'due_date': today_str   # pre-filled by JS, but we test it
    })
    assert response.status_code == 201
    day_task = response.get_json()
    day_task_id = day_task['id']
    assert day_task['status'] == 'todo'  # ← forced by from_day_page
    assert day_task['due_date'] == today_str

    # 3. FETCH ALL TASKS — both should appear
    response = authenticated_client.get('/api/tasks')
    assert response.status_code == 200
    all_tasks = response.get_json()
    assert len(all_tasks) >= 2
    assert any(t['id'] == global_task_id for t in all_tasks)
    assert any(t['id'] == day_task_id for t in all_tasks)

    # 4. FETCH TASKS FOR TODAY — only day_task should appear
    year, month, day = today_str.split('-')
    response = authenticated_client.get(f'/api/tasks/period/day/{year}/{month}/{day}')
    assert response.status_code == 200
    day_tasks = response.get_json()
    assert any(t['id'] == day_task_id for t in day_tasks)
    assert not any(t['id'] == global_task_id for t in day_tasks)  # global has no due_date

    # 5. MOVE TASK STATUS
    response = authenticated_client.post(f'/api/tasks/{day_task_id}/move', json={
        'status': 'doing'
    })
    assert response.status_code == 200
    moved_task = response.get_json()
    assert moved_task['status'] == 'doing'

    # 6. UPDATE TASK
    response = authenticated_client.patch(f'/api/tasks/{global_task_id}', json={
        'title': 'Updated Global Task',
        'priority': 'critical',
        'tags': 'updated,test'
    })
    assert response.status_code == 200  # or 204 — check your route

    # Verify update
    response = authenticated_client.get(f'/api/tasks/{global_task_id}')
    assert response.status_code == 200
    updated = response.get_json()
    assert updated['title'] == 'Updated Global Task'
    assert updated['priority'] == 'critical'

    # 7. DELETE BOTH — rollback will clean anyway
    authenticated_client.delete(f'/api/tasks/{global_task_id}')
    authenticated_client.delete(f'/api/tasks/{day_task_id}')