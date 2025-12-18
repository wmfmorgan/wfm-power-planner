# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'hulkamania-never-dies-2025')
    
    # FORCES IPv4 — POSTGRES ON WINDOWS LOVES THIS
    SQLALCHEMY_DATABASE_URI = 'postgresql://hulkster:whc2025!@127.0.0.1:5432/wfm_power_planner'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'connect_timeout': 10}
    }

    # app/config.py — ADD THIS CLASS
class TestConfig(Config):
    TESTING = True
    # Use your existing local DB — clutter away!
    SQLALCHEMY_DATABASE_URI = 'postgresql://hulkster:whc2025!@127.0.0.1:5432/wfm_power_planner'
    # Optional: disable some things for speed
    SQLALCHEMY_TRACK_MODIFICATIONS = False