# tests/test_goals_api.py — FINAL DOMINATION — LOGIN + FOLLOW REDIRECTS
import pytest
from flask import url_for

def test_create_and_get_goal(authenticated_client):
    # Optional: Force login via route first (ensures session cookie)
    login_response = authenticated_client.get('/login')  # Gets CSRF if any, but we have none
    # CREATE GOAL — follow_redirects=False to catch real status
    response = authenticated_client.post('/api/goals', json={
        'title': 'Test Domination Goal',
        'category': 'work',
        'timeframe': 'monthly'
    }, follow_redirects=True)  # ← KEY: Follow to get final 200
    
    assert response.status_code == 200
    data = response.get_json()
    goal_id = data['id']
    
    # GET TREE
    response = authenticated_client.get('/api/goals')
    assert response.status_code == 200
    tree = response.get_json()
    assert any(g['id'] == goal_id and g['title'] == 'Test Domination Goal' for g in tree)
    
    # DELETE
    authenticated_client.delete(f'/api/goals/{goal_id}')