# app/calendar_routes.py
# CALENDAR COMMAND CENTER — PHASE 2 BEGINS
from flask import Blueprint, render_template, jsonify, request, make_response
from flask_login import login_required
from datetime import datetime

calendar_bp = Blueprint('calendar', __name__, template_folder='templates/calendar')

@calendar_bp.route('/calendar')
@calendar_bp.route('/calendar/<view>')
@calendar_bp.route('/calendar/<view>/<int:year>')
@calendar_bp.route('/calendar/<view>/<int:year>/<int:month>')
@calendar_bp.route('/calendar/<view>/<int:year>/<int:month>/<int:day>')
@login_required
def calendar_view(view='month', year=None, month=None, day=None):
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    day = day or today.day

    valid_views = ['year', 'quarter', 'month', 'week', 'day']
    if view not in valid_views:
        view = 'month'

    context = {
        'current_view': view,
        'year': year,
        'month': month,
        'day': day,
        'today': today,
        'datetime': datetime,
    }
    # ADD THESE LINES — THIS IS THE FIX
    response = make_response(render_template('calendar/base_calendar.html', **context))
    response.headers.set('X-Current-View', view)
    response.headers.set('X-Current-Year', str(year))
    response.headers.set('X-Current-Month', str(month))
    response.headers.set('X-Current-Day', str(day))
    return response