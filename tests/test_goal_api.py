# tests/test_goal_api.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # project root

import pytest
from app import create_app
from app.extensions import db
from app.models.goal import Goal, GoalStatus, GoalCategory, GoalTimeframe
from flask_login import current_user
from app.models.user import User  # assuming you have this

@pytest.fixture
def app():
    """Create app with testing config"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Fast in-memory DB
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def authenticated_client(client, app):
    """Log in the single warrior (hulkster)"""
    with app.app_context():
        # Create test user — matches your Single Warrior Mode
        user = User(username="hulkster", email="hulk@wrestle.com")
        user.set_password("whc2025!")
        db.session.add(user)
        db.session.commit()

        # Log in
        with client.session_transaction() as sess:
            sess['user_id'] = user.id

        yield client

def test_create_goal_api(authenticated_client):
    """Test POST /api/goals creates a goal with correct defaults"""
    payload = {
        "title": "SQUASH 2025 LIKE A JOBBER",
        "description": "Total domination plan",
        "category": "health",
        "timeframe": "yearly"
    }

    response = authenticated_client.post(
        '/api/goals',
        json=payload,
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data['title'] == payload['title']
    assert data['description'] == payload['description']
    assert data['category'] == 'health'
    assert data['timeframe'] == 'yearly'
    assert data['status'] == 'todo'  # default
    assert data['progress'] == 0
    assert data['is_habit'] is False

    # Verify it's really in DB
    with authenticated_client.application.app_context():
        goal = Goal.query.filter_by(title=payload['title']).first()
        assert goal is not None
        assert goal.category == GoalCategory.HEALTH
        assert goal.timeframe == GoalTimeframe.YEARLY
        assert goal.status == GoalStatus.TODO