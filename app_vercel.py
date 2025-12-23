"""
Vercel-compatible version of app.py
Uses yt-dlp Python API instead of subprocess
"""
from flask import Flask, render_template, request, jsonify, send_file, Response
import json
import os
import re
import requests
import time
import hashlib
from urllib.parse import urlparse
from threading import Lock

# Try to import yt-dlp Python API
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("Warning: yt-dlp not available. Install with: pip install yt-dlp")

app = Flask(__name__)

# Configuration for Vercel (use /tmp for serverless)
DOWNLOAD_DIR = '/tmp/downloads' if os.path.exists('/tmp') else os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Cache configuration
CACHE_TTL = 3600  # 1 hour
cache = {}
cache_lock = Lock()

# Cleanup old files
CLEANUP_INTERVAL = 3600
last_cleanup = time.time()

def cleanup_old_files():
    """Remove files older than 1 hour"""
    global last_cleanup
    current_time = time.time()
    
    if current_time - last_cleanup < CLEANUP_INTERVAL:
        return
    
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > CLEANUP_INTERVAL:
                    os.remove(filepath)
        last_cleanup = current_time
    except Exception as e:
        print(f"Cleanup error: {e}")

def get_cache_key(url):
    """Generate cache key from URL"""
    return hashlib.md5(url.encode()).hexdigest()

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    filename = re.sub(r'&#\d+;', '', filename)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip()
    return filename[:200]

def get_video_info_optimized(url):
    """
    OPTIMIZED: Uses yt-dlp Python API instead of subprocess
    """
    if not YT_DLP_AVAILABLE:
        return None, "yt-dlp Python package not available. Please install: pip install yt-dlp"
    
    cache_key = get_cache_key(url)
    
    # Check cache
    with cache_lock:
        if cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if time.time() - cached_time < CACHE_TTL:
                return cached_data, None
    
    try:
        # Use yt-dlp Python API
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract video URL
            video_url = info.get('url')
            if not video_url and 'formats' in info and len(info['formats']) > 0:
                video_url = info['formats'][0].get('url')
            
            # Get size from HTTP headers
            size = 0
            if video_url:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = requests.head(video_url, headers=headers, timeout=5, allow_redirects=True)
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        size = int(content_length)
                except:
                    pass
            
            # Prepare response data
            response_data = {
                'info': info,
                'video_url': video_url,
                'size': size,
                'duration': info.get('duration', 0)
            }
            
            # Cache the result
            with cache_lock:
                cache[cache_key] = (response_data, time.time())
            
            return response_data, None
            
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_video():
    """Extract video information"""
    cleanup_old_files()
    
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    parsed = urlparse(url)
    if 'linkedin.com' not in parsed.netloc:
        return jsonify({'error': 'Please provide a valid LinkedIn URL'}), 400
    
    video_data, error = get_video_info_optimized(url)
    if error:
        return jsonify({'error': f'Failed to extract video: {error}'}), 500
    
    if not video_data:
        return jsonify({'error': 'No video found at this URL'}), 404
    
    info = video_data['info']
    video_url = video_data['video_url']
    size = video_data['size']
    duration = video_data['duration']
    
    if not size:
        size = info.get('filesize') or info.get('filesize_approx') or 0
    
    title = sanitize_filename(info.get('title', 'LinkedIn Video'))
    
    response = {
        'success': True,
        'title': title,
        'duration': int(duration) if duration else 0,
        'thumbnail': info.get('thumbnail') or (info.get('thumbnails', [{}])[0].get('url') if info.get('thumbnails') else None),
        'download_url': video_url,
        'size': int(size) if size else 0
    }
    
    return jsonify(response)

@app.route('/api/download-proxy')
def download_proxy():
    """Proxy endpoint that forces download"""
    video_url = request.args.get('url', '')
    filename = request.args.get('filename', 'linkedin_video.mp4')
    
    if not video_url:
        return jsonify({'error': 'Please provide a video URL'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(video_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            mimetype='video/mp4',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'video/mp4',
                'Content-Length': response.headers.get('Content-Length', '')
            }
        )
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to download video: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)

