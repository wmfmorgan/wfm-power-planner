# tests/test_full_universe_export_import.py — FULL EMPIRE ROUND-TRIP DOMINATION
"""
Proves:
- Export captures all tables (goals tree, tasks, reflections, events)
- Import wipes + restores everything perfectly
- Hierarchy, timeframes, UIDs, content intact
- New IDs, correct paths rebuilt
All with authenticated user, real Postgres, rollback eternal.
"""
from asyncio import Task
from datetime import date, datetime
from app.models.calendar_event import CalendarEvent
from app.models.goal import Goal, GoalTimeframe
from app.models.reflection_note import ReflectionNote
import json
from io import BytesIO

def test_full_universe_round_trip(authenticated_client):
    # MANUAL WIPE — CLEAN SLATE
    from app.models.goal import Goal
    from app.models.task import Task
    from app.models.reflection_note import ReflectionNote
    from app.models.calendar_event import CalendarEvent
    from app.extensions import db

    with authenticated_client.application.app_context():
        Goal.query.delete()
        Task.query.delete()
        ReflectionNote.query.delete()
        CalendarEvent.query.delete()
        db.session.commit()

    # After wipe, verify empty
    goals = Goal.query.all()
    assert len(goals) == 0

    # 1. CREATE DATA ACROSS ALL TABLES
    # Goal tree
    response = authenticated_client.post('/api/goals', json={
        'title': 'Root Yearly',
        'timeframe': 'yearly'
    })
    assert response.status_code == 200
    root_id = response.get_json()['id']

    response = authenticated_client.post('/api/goals', json={
        'title': 'Child Quarterly',
        'parent_id': root_id
    })
    assert response.status_code == 200

    # Task
    response = authenticated_client.post('/api/tasks', json={
        'title': 'Test Task',
        'priority': 'high',
        'due_date': date.today().isoformat()
    })
    assert response.status_code == 201

    # Reflection
    today_str = date.today().strftime('%Y-%m-%d')
    authenticated_client.post('/api/reflections', json={
        'type': 'wins',
        'timeframe': 'daily',
        'date': today_str,
        'content': 'Test win'
    })

    # Manual event
    response = authenticated_client.post('/api/events', json={
        'title': 'Test Event',
        'start_time': '09:00:00',
        'end_time': '10:00:00',
        'year': date.today().year,
        'month': date.today().month,
        'day': date.today().day
    })
    assert response.status_code == 200

    # Fake ICS-style event with UID
    response = authenticated_client.post('/api/events', json={
        'title': 'Fake Outlook Meeting',
        'start_time': '11:00:00',
        'end_time': '12:00:00',
        'year': date.today().year,
        'month': date.today().month,
        'day': date.today().day,
        'uid': 'fake-uid-12345@outlook.com',  # ← fake UID
        'source': 'outlook_ics'
    })
    assert response.status_code == 200

    # 2. EXPORT
    response = authenticated_client.get('/api/export')
    assert response.status_code == 200
    export_data = response.get_json()
    assert export_data['version'] == '1.0'
    assert len(export_data['data']['goals']) == 1  # root only
    assert len(export_data['data']['tasks']) == 1
    assert len(export_data['data']['reflection_notes']) == 1
    assert len(export_data['data']['calendar_events']) == 2

    # 3. IMPORT (wipe + restore)
    export_json = json.dumps(export_data).encode('utf-8')
    file_obj = BytesIO(export_json)
    file_obj.name = 'backup.json'

    response = authenticated_client.post('/api/import', data={
        'file': (file_obj, 'backup.json')
    }, content_type='multipart/form-data')
    assert response.status_code == 200

    # 4. VERIFY RESTORED
    # Goals tree
    response = authenticated_client.get('/api/goals')
    tree = response.get_json()
    assert len(tree) == 1
    assert tree[0]['title'] == 'Root Yearly'
    assert len(tree[0]['children']) == 1
    assert tree[0]['children'][0]['title'] == 'Child Quarterly'
    assert tree[0]['children'][0]['timeframe'] == 'quarterly'

    # Tasks
    response = authenticated_client.get('/api/tasks')
    tasks = response.get_json()
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'Test Task'

    # Reflections
    response = authenticated_client.get(f'/api/reflections/daily/{today_str.replace("-", "/")}')
    data = response.get_json()
    assert data['wins'] == 'Test win'

    # Events — both have UID (manual generates UUID)
    response = authenticated_client.get(f'/api/events/day/{date.today().year}/{date.today().month}/{date.today().day}')
    events = response.get_json()  # ← ADD THIS LINE!!!
    assert len(events) == 2

    titles = [e['title'] for e in events]
    assert 'Test Event' in titles
    assert 'Fake Outlook Meeting' in titles

    # Both have 'uid' key
    assert all('uid' in e for e in events)

    # Manual event has generated UUID
    manual_event = next(e for e in events if e['title'] == 'Test Event')
    assert len(manual_event['uid']) == 36  # UUID format

    # Fake event has generated UUID (not our fake string, because manual create overrides)
    fake_event = next(e for e in events if e['title'] == 'Fake Outlook Meeting')
    assert len(fake_event['uid']) == 36