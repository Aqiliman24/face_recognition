from flask import Blueprint, render_template, current_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

views = Blueprint('views', __name__)

@views.route('/')
def home():
    """Render the home page with webcam interface for face verification."""
    logger.info("Rendering home page")
    return render_template('index.html')

@views.route('/register')
def register():
    """Render the page for registering new faces."""
    logger.info("Rendering registration page")
    return render_template('register.html')
