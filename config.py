import os
from datetime import timedelta
import pytz

class Config:
    """Configuración base de la aplicación"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///inventario.db")
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_TABLES = os.environ.get('AUTO_CREATE_TABLES', 'true').lower() == 'true'
    PAGES_ORIGIN = os.environ.get('PAGES_ORIGIN', 'https://azaerodiego.github.io')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Zona horaria (Perú: UTC-5)
    TIMEZONE = pytz.timezone('America/Lima')
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de carga de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    AUTO_CREATE_TABLES = os.environ.get('AUTO_CREATE_TABLES', 'false').lower() == 'true'


class TestingConfig(Config):
    """Configuración para pruebas"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
