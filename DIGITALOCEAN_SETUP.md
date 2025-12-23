# DigitalOcean App Platform Setup Guide

## 🚀 Step-by-Step Deployment

### Prerequisites
- GitHub repository (already done ✅)
- DigitalOcean account (create at https://www.digitalocean.com)

---

## 📋 Step 1: Create DigitalOcean App

1. **Login to DigitalOcean**
   - Go to: https://cloud.digitalocean.com
   - Sign up/login

2. **Create New App**
   - Click "Create" → "Apps"
   - Select "GitHub" as source
   - Authorize DigitalOcean to access GitHub
   - Select your repository: `neerajdeveloper/linkedin-video-downloader`
   - Click "Next"

---

## ⚙️ Step 2: Configure App

### Auto-Detection:
- DigitalOcean will auto-detect Python/Flask
- It should detect `requirements.txt`

### Manual Configuration (if needed):

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `gunicorn app:app --bind 0.0.0.0:8080`
- **Environment:** Python 3.11+

**Environment Variables:**
- `FLASK_DEBUG=false`
- `PORT=8080` (DigitalOcean sets this automatically)

---

## 🔧 Step 3: Install yt-dlp

### Option A: Python Package (Recommended)
Add to `requirements.txt`:
```txt
yt-dlp==2025.12.8
```

### Option B: System Package (via Build Command)
In App Settings → Components:
- Add "Run Command" component
- Command: `apt-get update && apt-get install -y yt-dlp`

**Recommendation:** Use Option A (Python package) - simpler and more reliable.

---

## 📝 Step 4: Update app.py for Production

Make sure your `app.py` uses:
- Port from environment: `os.getenv('PORT', 5001)`
- Production-ready settings

**Current app.py should work, but verify:**

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
```

---

## 🚀 Step 5: Deploy

1. **Review Settings**
   - Check build command
   - Check run command
   - Verify environment variables

2. **Deploy**
   - Click "Create Resources"
   - Wait for build (~2-5 minutes)
   - Your app will be live!

---

## 🌐 Step 6: Access Your App

- DigitalOcean provides a URL like: `https://your-app-name.ondigitalocean.app`
- Share this URL!

---

## 💰 Pricing

**App Platform:**
- **Basic Plan:** $5/month
- **Professional Plan:** $12/month (more resources)

**What you get:**
- 512MB RAM (Basic) or 1GB (Pro)
- 1GB storage
- Auto-scaling
- GitHub integration
- SSL certificates (free)

---

## 🔄 Updates

**Automatic:**
- Push to GitHub → Auto-deploys
- DigitalOcean watches your repo

**Manual:**
- Go to App → Settings → Deployments
- Click "Create Deployment"

---

## 🐛 Troubleshooting

### Build Fails:
- Check build logs in DigitalOcean dashboard
- Verify `requirements.txt` is correct
- Ensure Python version is compatible

### App Crashes:
- Check runtime logs
- Verify yt-dlp is installed
- Check environment variables

### yt-dlp Not Found:
- Add to `requirements.txt`: `yt-dlp==2025.12.8`
- Or add build command to install system package

---

## ✅ Checklist

- [ ] DigitalOcean account created
- [ ] App created from GitHub repo
- [ ] Build command configured
- [ ] Run command configured (gunicorn recommended)
- [ ] yt-dlp added to requirements.txt
- [ ] Environment variables set
- [ ] App deployed successfully
- [ ] Test video extraction works

---

## 🎯 Why DigitalOcean App Platform?

✅ **No timeout limits** - Can handle long video extractions
✅ **Full subprocess support** - yt-dlp works perfectly
✅ **Writable filesystem** - Can download/store files
✅ **Traditional Flask** - Works exactly like local
✅ **Easy setup** - Similar to Heroku
✅ **Affordable** - $5/month
✅ **Auto-deploy** - Push to GitHub = auto-deploy

**Perfect for your LinkedIn Video Downloader!** 🚀

