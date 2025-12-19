# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'hulkamania-never-dies-2025')  # Render generates secure one

    # Prod: Use Render's DATABASE_URL; Dev: fallback to local
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'postgresql://hulkster:whc2025!@127.0.0.1:5432/wfm_power_planner'

    # Fix Render's "postgres://" prefix for SQLAlchemy
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'connect_timeout': 10}
    }
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://hulkster:whc2025!@127.0.0.1:5432/wfm_power_planner'
    SQLALCHEMY_TRACK_MODIFICATIONS = False