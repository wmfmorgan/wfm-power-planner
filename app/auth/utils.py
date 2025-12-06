# app/auth/utils.py
from flask import current_app
from app.extensions import bcrypt

def hash_password(pw):
    return bcrypt.generate_password_hash(pw).decode('utf-8')

def check_password(pw, hashed):
    return bcrypt.check_password_hash(hashed, pw)