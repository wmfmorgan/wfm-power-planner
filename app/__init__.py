# app/__init__.py
# THE ONE AND ONLY APP FACTORY — CLEAN, ETERNAL, CHAMPIONSHIP-CALIBER
from flask import Flask, render_template
from flask import Flask
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate

from .config import Config
from .extensions import db, login_manager, bcrypt

# BLUEPRINTS — IMPORTED ONCE, REGISTERED ONCE
from .auth_routes import auth_bp
from .goals_routes import goals_bp

# MODELS — ONLY FOR USER LOADER
from .models.user import User

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['TEMPLATES_AUTO_RELOAD'] = True   # ← THIS LINE
    app.jinja_env.auto_reload = True             # ← AND THIS LINE
    app.config.from_object(Config)

    # === EXTENSIONS ===
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    # === BLUEPRINT REGISTRATION — THE ETERNAL ORDER ===
    app.register_blueprint(auth_bp)      # /auth/login, /auth/logout
    app.register_blueprint(goals_bp)     # /goals, /api/goals

    # === DASHBOARD ROUTE ===
    @app.route('/')
    @app.route('/index')
    @login_required
    def index():
        return render_template('index.html')

    # === USER LOADER ===
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.template_filter('date_format')
    def date_format(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d')

    return app

