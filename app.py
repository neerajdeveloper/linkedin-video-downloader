from flask import Flask, render_template, request, jsonify, send_file, Response
import subprocess
import json
import os
import re
import requests
import time
import hashlib
from urllib.parse import urlparse
from functools import lru_cache
from threading import Lock

app = Flask(__name__)

# Configuration
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Cache configuration
CACHE_TTL = 3600  # 1 hour
cache = {}
cache_lock = Lock()

# Cleanup old files (older than 1 hour)
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

def _format_linkedin_error(error_msg, url):
    """Format user-friendly error messages for LinkedIn videos"""
    if "Unable to extract video" in error_msg:
        return (
            "Unable to extract this LinkedIn video. This might be because:\n"
            "• The video is private or restricted\n"
            "• The video requires LinkedIn login\n"
            "• LinkedIn has changed their video format\n\n"
            "Try:\n"
            "• Making sure the video is public\n"
            "• Using a different LinkedIn video URL\n"
            "• Checking if you're logged into LinkedIn when accessing the video"
        )
    elif "Private video" in error_msg or "private" in error_msg.lower():
        return (
            "This video appears to be private or restricted. "
            "Please ensure the video is publicly accessible."
        )
    else:
        return error_msg

def get_video_info_optimized(url):
    """
    OPTIMIZED: Single yt-dlp call to get all info at once
    This replaces 3-4 separate calls
    """
    cache_key = get_cache_key(url)
    
    # Check cache
    with cache_lock:
        if cache_key in cache:
            cached_data, cached_time = cache[cache_key]
            if time.time() - cached_time < CACHE_TTL:
                return cached_data, None
    
    # Try multiple extraction methods
    methods = [
        # Method 1: Standard extraction
        {
            'cmd': [
                'yt-dlp',
                '--format', 'best[ext=mp4]/best',
                '--dump-json',
                '--no-warnings',
                url
            ]
        },
        # Method 2: Try without format restriction
        {
            'cmd': [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                url
            ]
        },
        # Method 3: Try with best format only
        {
            'cmd': [
                'yt-dlp',
                '--format', 'best',
                '--dump-json',
                '--no-warnings',
                url
            ]
        }
    ]
    
    last_error = None
    
    for method_idx, method in enumerate(methods):
        try:
            result = subprocess.run(
                method['cmd'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    info = json.loads(result.stdout)
                    
                    # Extract video URL from info
                    video_url = info.get('url')
                    if not video_url and 'formats' in info and len(info['formats']) > 0:
                        # Try to get URL from formats array
                        video_url = info['formats'][0].get('url')
                    
                    # Get size from HTTP headers (async, non-blocking)
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
                    
                except json.JSONDecodeError:
                    last_error = "Failed to parse video information."
                    continue
            else:
                # Store error but try next method
                error_msg = result.stderr.strip()
                if "Unable to extract video" in error_msg or "Private video" in error_msg:
                    last_error = _format_linkedin_error(error_msg, url)
                else:
                    last_error = error_msg
                continue
                
        except subprocess.TimeoutExpired:
            last_error = "Request timed out. Please try again."
            continue
        except Exception as e:
            last_error = str(e)
            continue
    
    # All methods failed
    return None, last_error or "Failed to extract video. The video may be private or require authentication."

def _format_linkedin_error(error_msg, url):
    """Format user-friendly error messages for LinkedIn videos"""
    if "Unable to extract video" in error_msg:
        return (
            "Unable to extract this LinkedIn video. This might be because:\n"
            "• The video is private or restricted\n"
            "• The video requires LinkedIn login\n"
            "• LinkedIn has changed their video format\n\n"
            "Try:\n"
            "• Making sure the video is public\n"
            "• Using a different LinkedIn video URL\n"
            "• Checking if you're logged into LinkedIn when accessing the video"
        )
    elif "Private video" in error_msg or "private" in error_msg.lower():
        return (
            "This video appears to be private or restricted. "
            "Please ensure the video is publicly accessible."
        )
    else:
        return error_msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_video():
    """Extract video information - OPTIMIZED VERSION"""
    # Cleanup old files periodically
    cleanup_old_files()
    
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    # Better URL validation
    parsed = urlparse(url)
    if 'linkedin.com' not in parsed.netloc:
        return jsonify({'error': 'Please provide a valid LinkedIn URL'}), 400
    
    # Single optimized call
    video_data, error = get_video_info_optimized(url)
    if error:
        return jsonify({'error': f'Failed to extract video: {error}'}), 500
    
    if not video_data:
        return jsonify({'error': 'No video found at this URL'}), 404
    
    info = video_data['info']
    video_url = video_data['video_url']
    size = video_data['size']
    duration = video_data['duration']
    
    # Fallback size check
    if not size:
        size = info.get('filesize') or info.get('filesize_approx') or 0
    
    # Prepare response
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
    """Proxy endpoint that forces download instead of opening in browser"""
    video_url = request.args.get('url', '')
    filename = request.args.get('filename', 'linkedin_video.mp4')
    
    if not video_url:
        return jsonify({'error': 'Please provide a video URL'}), 400
    
    try:
        # Stream the video with download headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(video_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create Flask response with download headers
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

@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video and serve it"""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    try:
        # Use cached info if available
        video_data, error = get_video_info_optimized(url)
        if error or not video_data:
            filename = 'linkedin_video.mp4'
        else:
            title = sanitize_filename(video_data['info'].get('title', 'linkedin_video'))
            filename = f"{title}.mp4"
        
        # Download video
        temp_file = os.path.join(DOWNLOAD_DIR, filename)
        
        cmd = [
            'yt-dlp',
            '--format', 'best[ext=mp4]/best',
            '--output', temp_file,
            '--no-warnings',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return jsonify({'error': f'Download failed: {result.stderr}'}), 500
        
        # Find downloaded file
        if not os.path.exists(temp_file):
            base_name = temp_file.replace('.mp4', '')
            for ext in ['.mp4', '.webm', '.m4a']:
                if os.path.exists(base_name + ext):
                    temp_file = base_name + ext
                    break
        
        if not os.path.exists(temp_file):
            return jsonify({'error': 'Downloaded file not found'}), 500
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Download timed out'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use environment variable for debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)

