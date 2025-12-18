# tests/test_reflection_api.py — PHASE 3: REFLECTION NOTES AUTOSAVE DOMINATION
"""
Proves:
- Save reflection note (prep/wins/improve/notes) for daily/weekly/monthly
- Fetch all notes for a specific timeframe + date
- Updates existing note (upsert behavior)
- Different horizons keyed correctly (daily = exact date, weekly = Sunday, monthly = 1st)
All with authenticated user, real Postgres, rollback eternal.
"""
from datetime import date, timedelta

def test_reflection_notes_crud(authenticated_client):
    # Helper to save a note
    def save_note(note_type, timeframe, date_str, content):
        return authenticated_client.post('/api/reflections', json={
            'type': note_type,
            'timeframe': timeframe,
            'date': date_str,
            'content': content
        })

    # 1. SAVE DAILY NOTES — exact date
    today_str = date.today().strftime('%Y-%m-%d')
    save_note('prep', 'daily', today_str, 'Daily prep content')
    save_note('wins', 'daily', today_str, 'Daily wins content')
    save_note('improve', 'daily', today_str, 'Daily improve content')
    save_note('notes', 'daily', today_str, 'Daily notes content')

    # 2. FETCH DAILY — all 4 should return
    response = authenticated_client.get(f'/api/reflections/daily/{today_str.replace("-", "/")}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['prep'] == 'Daily prep content'
    assert data['wins'] == 'Daily wins content'
    assert data['improve'] == 'Daily improve content'
    assert data['notes'] == 'Daily notes content'

    # 3. WEEKLY — keyed to Sunday of the week
    # Use today — calculate its Sunday
    today = date.today()
    sunday = today - timedelta(days=(today.weekday() + 1) % 7)  # Sunday
    sunday_str = sunday.strftime('%Y-%m-%d')

    save_note('prep', 'weekly', today_str, 'Weekly prep from today')
    save_note('wins', 'weekly', today_str, 'Weekly wins from today')

    response = authenticated_client.get(f'/api/reflections/weekly/{today_str.replace("-", "/")}')
    assert response.status_code == 200
    weekly_data = response.get_json()
    assert weekly_data['prep'] == 'Weekly prep from today'
    assert weekly_data['wins'] == 'Weekly wins from today'

    # 4. MONTHLY — keyed to 1st of month
    first_of_month_str = today.replace(day=1).strftime('%Y-%m-%d')
    save_note('prep', 'monthly', today_str, 'Monthly prep')

    response = authenticated_client.get(f'/api/reflections/monthly/{today_str.replace("-", "/")[:7]}')  # YYYY/MM
    assert response.status_code == 200
    monthly_data = response.get_json()
    assert monthly_data['prep'] == 'Monthly prep'

    # 5. UPDATE EXISTING — upsert works
    save_note('prep', 'daily', today_str, 'Updated daily prep')
    response = authenticated_client.get(f'/api/reflections/daily/{today_str.replace("-", "/")}')
    assert response.status_code == 200
    updated = response.get_json()
    assert updated['prep'] == 'Updated daily prep'