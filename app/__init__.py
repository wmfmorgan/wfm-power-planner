# app/__init__.py
# THE ONE AND ONLY APP FACTORY — CLEAN, ETERNAL, CHAMPIONSHIP-CALIBER
from flask import Flask, render_template, request
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
    
    from app.date_utils import get_iso_week_for_goal, get_iso_year_for_goal

    @app.template_filter('iso_week')
    def iso_week_filter(year, month, day):
        return get_iso_week_for_goal(int(year), int(month), int(day))

    @app.template_filter('first_day_weekday')
    def first_day_weekday_filter(year, month):
        """
        Return weekday of the 1st of the given month
        0 = Monday, 1 = Tuesday, ..., 6 = Sunday
        """
        d = date(int(year), int(month), 1)
        # Python: 0=Mon ... 6=Sun → we want 6=Sun, so just return it!
        return d.weekday()

    @app.context_processor
    def inject_calendar_data():
        if request.endpoint and request.endpoint.startswith('calendar.'):
            view_args = request.view_args or {}
            view = view_args.get('view', 'month')
            year = view_args.get('year') or datetime.today().year
            month = view_args.get('month') or datetime.today().month
            day = view_args.get('day')  # can be None

            if view == 'monthly':
                date_str = f"{year}-{month:02d}-01"
            elif view == 'weekly':
                day_for_str = day if day is not None else 1
                date_str = f"{year}-{month:02d}-{day_for_str:02d}"
            else:  # daily
                day_for_str = day if day is not None else 1
                date_str = f"{year}-{month:02d}-{day_for_str:02d}"

            timeframe_map = {
            'day': 'daily',
            'week': 'weekly',
            'month': 'monthly',
            'year': 'monthly',      # fallback if we ever add year view
            'quarter': 'monthly',   # fallback
            }
            timeframe_enum = timeframe_map.get(view, 'monthly')

            return {
                'calendar_view': view,
                'calendar_year': year,
                'calendar_month': month,
                'calendar_day': day,
                'calendar_timeframe': timeframe_enum,
                'calendar_date_str': date_str
            }
        return {}
    return app