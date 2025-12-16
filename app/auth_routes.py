# app/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # MAX session lifetime — remember forever unless explicit logout
            login_user(user, remember=True)
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        if password != confirm:
            flash('Passwords do not match, brother!', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken — choose another, warrior!', 'danger')
            return render_template('auth/register.html')
        
        # Create the new champion
        new_user = User(username=username)
        new_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.add(new_user)
        db.session.commit()
        
        # Auto-login and max session
        login_user(new_user, remember=True)
        flash(f'Welcome to the empire, {username}! Hulkamania runs wild!', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out — come back stronger, brother!', 'info')
    return redirect(url_for('auth.login'))