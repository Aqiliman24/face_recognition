import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    # Create and configure the app
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # App configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    app.config['USE_S3'] = os.environ.get('USE_S3', 'false').lower() == 'true'
    app.config['AWS_BUCKET'] = os.environ.get('AWS_BUCKET', '')
    app.config['FACES_DIR'] = os.environ.get('FACES_DIR', './faces')
    
    # Register blueprints
    from app.routes.views import views
    from app.routes.api import api
    
    app.register_blueprint(views)
    app.register_blueprint(api)
    
    return app
