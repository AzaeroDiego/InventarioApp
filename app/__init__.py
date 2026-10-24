from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import MetaData
from config import config
import os

# En PostgreSQL/Supabase, usar explícitamente el schema inventario.
# En SQLite este schema no se usa, porque config.py mantiene SQLite solo si no hay DATABASE_URL.
db = SQLAlchemy(metadata=MetaData(schema="inventario"))
login_manager = LoginManager()

def create_app(config_name='development'):
    """Factory function para crear la aplicación Flask"""
    # Especificar la ruta correcta a templates y static
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    if config_name == 'production':
        if not app.config['SQLALCHEMY_DATABASE_URI'].startswith(('postgresql:', 'postgresql+')):
            raise RuntimeError('Producción requiere DATABASE_URL de PostgreSQL; SQLite es solo para pruebas locales.')
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise RuntimeError('Configura SECRET_KEY en tu servidor de producción.')
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith(('postgresql:', 'postgresql+psycopg2:')):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            **app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}),
            'pool_recycle': 300,
            'connect_args': {'connect_timeout': 8}
        }
    
    # Crear carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Inicializar extensiones
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            **app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}),
            'execution_options': {'schema_translate_map': {'inventario': None}}
        }
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    
    # Registrar blueprints
    from app.auth import auth_bp
    from app.analytics import analytics_bp
    from app.main import main_bp
    from app.api import api_bp
    from app.barra import barra_bp
    
    app.register_blueprint(auth_bp)
    # Analytics se registra antes de main para reemplazar /dashboard y /reportes.
    app.register_blueprint(analytics_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(barra_bp)
    from app.pages_api import pages_bp
    app.register_blueprint(pages_bp)
    
    # Crear tablas de base de datos
    if app.config.get('AUTO_CREATE_TABLES', True):
        with app.app_context():
            db.create_all()
    
    return app
