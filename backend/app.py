import sys
import os

# Make sure database module is importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from flask import Flask
from flask_cors import CORS
from routes import bp
import db

app = Flask(__name__)

# Allow requests from the frontend (adjust origin in production)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register all API routes under /api prefix
app.register_blueprint(bp, url_prefix='/api')


if __name__ == '__main__':
    print("🌱 Initialising MindSprout database...")
    db.init_db()
    print("🚀 Starting MindSprout Flask server on http://localhost:5000")
    app.run(debug=True, port=5000)