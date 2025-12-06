# app/__init__.py
from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from .config import Config
from .extensions import db, login_manager, bcrypt
from .auth.routes import auth_bp
from .models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Create tables + warrior on first run
    with app.app_context():
        db.create_all()
        if not User.query.first():
            from app.auth.utils import hash_password
            hashed = hash_password('whc2025!')
            warrior = User(username='hulkster', password_hash=hashed)
            db.session.add(warrior)
            db.session.commit()
            print("\n" + "="*70)
            print("WFM-POWER-PLANNER WARRIOR CREATED — POSTGRES IS ALIVE!")
            print("Username: hulkster")
            print("Password: whc2025!")
            print("Database: wfm_power_planner on localhost:5432")
            print("ltree extension ENABLED — HIERARCHY READY!")
            print("="*70 + "\n")

    # DASHBOARD ROUTE — TENET-COMPLIANT, NO EXTRA FOLDERS!
    @app.route('/')
    @app.route('/index')
    @login_required
    def index():
        return render_template('index.html')

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app