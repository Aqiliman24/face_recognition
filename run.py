from app import create_app
import datetime
import os

app = create_app()

# Add template context processor for current year
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

if __name__ == '__main__':
    print("Starting Flask app with debugging enabled...")
    print(f"FACES_DIR set to: {app.config['FACES_DIR']}")
    # Create faces directory if it doesn't exist
    faces_dir = app.config['FACES_DIR']
    os.makedirs(faces_dir, exist_ok=True)
    
    # Run the application
    app.run(host='0.0.0.0', port=2020, debug=True)