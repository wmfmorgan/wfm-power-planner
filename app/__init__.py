# app/__init__.py
# THE ONE AND ONLY APP FACTORY — CLEAN, ETERNAL, CHAMPIONSHIP-CALIBER
from flask import Flask, render_template
from flask import Flask
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate

from .config import Config
from .extensions import db, login_manager, bcrypt
from datetime import datetime
from calendar import monthrange
from datetime import date

# BLUEPRINTS — IMPORTED ONCE, REGISTERED ONCE
from .auth_routes import auth_bp
from .goals_routes import goals_bp
from .calendar_routes import calendar_bp
from .tasks_routes import tasks_bp

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
    app.register_blueprint(calendar_bp)
    app.register_blueprint(tasks_bp)
    
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
    
    @app.template_filter('month_name')
    def month_name(month_number):
        return datetime(2000, month_number, 1).strftime('%B')
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    @app.template_filter('days_in_month')
    def days_in_month(year, month):
        """Return number of days in given year/month — used by month grid"""
        return monthrange(int(year), int(month))[1]
    
    @app.template_filter('iso_week')
    def iso_week_filter(year, month, day):      
        """Return ISO week number, but prefer current-year bias (Dec 29-31 = week 53, not 1)"""
        from datetime import date

        d = date(int(year), int(month), int(day))
        iso_year, iso_week, _ = d.isocalendar()

        # If it's Dec 29-31 and ISO says next year → use previous week (53)
        if month == 12 and day >= 29 and iso_year == year + 1:
            return 53
        # If it's Jan 1-3 and ISO says previous year → use week 1 of current year
        elif month == 1 and day <= 3 and iso_year == year - 1:
            return 1

        return iso_week

    @app.template_filter('first_day_weekday')
    def first_day_weekday_filter(year, month):
        """
        Return weekday of the 1st of the given month
        0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        """
        d = date(int(year), int(month), 1)
        # Python: 0=Mon ... 6=Sun → we want 6=Sun, so just return it!
        return d.weekday()

    return app

