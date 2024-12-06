import os

class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MODEL_PATH = 'safety_gear_detection_app/models/ppe.pt'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
