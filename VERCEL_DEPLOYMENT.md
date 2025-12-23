# Vercel Deployment Guide

## ⚠️ Important Limitations

**Vercel has limitations that affect this app:**

1. **yt-dlp subprocess calls** - Vercel serverless functions have limited subprocess support
2. **File system** - Read-only filesystem (can't write to `/tmp` easily)
3. **Timeout** - 10 seconds on free tier, 30 seconds on Pro
4. **Binary dependencies** - yt-dlp needs to be installed as a Python package

## 🔧 Solution: Use Python yt-dlp Package

Instead of calling `yt-dlp` as a subprocess, we need to use it as a Python library.

### Step 1: Update requirements.txt

Add yt-dlp as a Python package:

```txt
Flask==3.0.0
Werkzeug==3.0.1
requests==2.31.0
yt-dlp==2025.12.8
```

### Step 2: Update app.py to use yt-dlp Python API

Replace subprocess calls with direct Python API calls.

## 🚀 Deployment Steps

### Option 1: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# For production
vercel --prod
```

### Option 2: Deploy via GitHub Integration

1. Connect your GitHub repo to Vercel
2. Vercel will auto-detect Python
3. Build settings:
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

## 📝 Required Files

- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Serverless function handler
- ✅ `requirements.txt` - Python dependencies (must include yt-dlp)
- ✅ `app.py` - Flask application

## ⚠️ Known Issues

1. **yt-dlp subprocess** - Won't work in Vercel. Need to use Python API.
2. **File downloads** - Limited by serverless function timeout
3. **Large videos** - May timeout on free tier

## 🔄 Alternative: Use Railway or Render

For better compatibility:
- **Railway** - Better for Flask apps with subprocess
- **Render** - Supports traditional Flask deployment
- **Heroku** - Classic Flask hosting (paid)

## 💡 Quick Fix for Current Error

The crash is likely because:
1. Missing `vercel.json` configuration
2. App not configured as serverless function
3. yt-dlp subprocess not available

**Immediate fix:** Add the files I created and redeploy.

