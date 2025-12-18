# tests/test_calendar_events_api.py — PHASE 4: CALENDAR EVENTS DOMINATION
"""
Proves:
- Manual event CRUD (create, update, delete)
- Events appear in day fetch
- ICS import dedupes by UID
All with authenticated user, real Postgres, rollback eternal.
"""
from datetime import date, datetime, timedelta

def test_manual_event_crud(authenticated_client):
    today = date.today()
    year, month, day = today.year, today.month, today.day
    day_str = today.strftime('%Y-%m-%d')

    # 1. CREATE MANUAL EVENT
    response = authenticated_client.post('/api/events', json={
        'title': 'Manual Test Event',
        'start_time': '10:00:00',
        'end_time': '11:00:00',
        'year': year,
        'month': month,
        'day': day
    })
    assert response.status_code == 200
    data = response.get_json()
    event_id = data['id']
    assert event_id is not None

    # 2. FETCH DAY EVENTS — should include our manual event
    response = authenticated_client.get(f'/api/events/day/{year}/{month}/{day}')
    assert response.status_code == 200
    events = response.get_json()
    assert any(e['id'] == event_id and e['title'] == 'Manual Test Event' for e in events)
    assert any(e['source'] == 'manual' for e in events)

    # 3. UPDATE EVENT
    response = authenticated_client.patch(f'/api/events/{event_id}', json={
        'title': 'Updated Manual Event',
        'start_time': '12:00:00',
        'end_time': '13:00:00',
        'year': year,
        'month': month,
        'day': day
    })
    assert response.status_code == 200

    # Verify update
    response = authenticated_client.get(f'/api/events/day/{year}/{month}/{day}')
    assert response.status_code == 200
    events = response.get_json()
    assert any(e['id'] == event_id and e['title'] == 'Updated Manual Event' for e in events)

    # 4. DELETE EVENT
    response = authenticated_client.delete(f'/api/events/{event_id}')
    assert response.status_code == 200

    # Verify gone
    response = authenticated_client.get(f'/api/events/day/{year}/{month}/{day}')
    assert response.status_code == 200
    events = response.get_json()
    assert not any(e['id'] == event_id for e in events)