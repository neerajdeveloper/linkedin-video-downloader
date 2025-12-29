"""
Vercel serverless function wrapper for Flask app
This file is required for Vercel deployment
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Vercel-compatible Flask app
try:
    from app_vercel import app
except ImportError as e:
    # Fallback error handling
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Import error: {str(e)}. Please check app_vercel.py", 500

# Vercel expects the app to be exported directly
# The @vercel/python runtime automatically wraps Flask apps

