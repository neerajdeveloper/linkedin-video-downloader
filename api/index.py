"""
Vercel serverless function wrapper for Flask app
This file is required for Vercel deployment
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Vercel-compatible Flask app
# CRITICAL: Only import app_vercel, NEVER import app.py
import sys
import os

# Prevent any accidental import of app.py
if 'app' in sys.modules:
    del sys.modules['app']

try:
    # Explicitly import app_vercel
    from app_vercel import app
    print("✅ Successfully imported app_vercel")
except ImportError as e:
    # Better error handling for Vercel
    import traceback
    error_msg = f"Import error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    print(f"❌ ERROR: {error_msg}")  # This will show in Vercel logs
    
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"<h1>Import Error</h1><pre>{error_msg}</pre>", 500
    
    @app.route('/<path:path>')
    def catch_all(path):
        return f"<h1>Import Error</h1><pre>{error_msg}</pre>", 500

# Vercel expects the app to be exported directly
# The @vercel/python runtime automatically wraps Flask apps

