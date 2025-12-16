# tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.goal import Goal
from flask_login import login_user
from sqlalchemy import String

# MONKEY PATCH CONFIG BEFORE create_app() RUNS — PURE PROTEIN
import app.config
app.config.Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
app.config.Config.SQLALCHEMY_ENGINE_OPTIONS = {}

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-2025'

    with app.app_context():
        # Replace Goal.path with String BEFORE mapper configuration
        # Delete the original LtreeType column
        del Goal.path
        # Add String version

        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_client(client, app):
    with app.app_context():
        user = User(username="hulkster")
        user.password_hash = "fakehash123"
        db.session.add(user)
        db.session.commit()

        with client:
            login_user(user)
            yield client