# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))  # Fixed: was 'main.index'
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')  # ← THIS WAS THE ONLY PROBLEM

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))