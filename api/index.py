"""
Vercel serverless function wrapper for Flask app
This file is required for Vercel deployment
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Vercel-compatible Flask app
from app_vercel import app

# Vercel serverless function handler
# This is the entry point Vercel will use
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, request.start_response)

# Export app for Vercel
__all__ = ['app', 'handler']

