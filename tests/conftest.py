# tests/conftest.py — MINIMAL GREEN — NO DB_SESSION FIXTURE
import pytest
from app import create_app
from app.extensions import db as _db, bcrypt
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.from_object('app.config.TestConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def authenticated_client(client, app):
    with app.app_context():
        # Create test user if not exists
        user = User.query.filter_by(username='testwarrior').first()
        if not user:
            user = User(username='testwarrior')
            user.password_hash = bcrypt.generate_password_hash('test123').decode('utf-8')
            _db.session.add(user)
            _db.session.commit()

        # Login via route — sets cookie perfectly
        response = client.post('/login', data={
            'username': 'testwarrior',
            'password': 'test123'
        }, follow_redirects=True)
        assert response.status_code == 200

    return client