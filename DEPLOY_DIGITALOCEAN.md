# 🚀 DigitalOcean Deployment - Quick Start

## ✅ Pre-Deployment Checklist

Your app is ready! Here's what's already configured:

- ✅ `requirements.txt` - Includes all dependencies (yt-dlp, Flask, gunicorn)
- ✅ `Procfile` - Configured for gunicorn
- ✅ `app.py` - Uses PORT from environment variable
- ✅ Templates and static files ready

## 📋 Step-by-Step Deployment

### 1. Create DigitalOcean Account
- Go to: https://cloud.digitalocean.com
- Sign up (get $200 credit for 60 days with referral)

### 2. Create New App
1. Click **"Create"** → **"Apps"**
2. Select **"GitHub"** as source
3. Authorize DigitalOcean to access your GitHub
4. Select your repository
5. Click **"Next"**

### 3. Configure App Settings

DigitalOcean will auto-detect Python/Flask, but verify these settings:

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `gunicorn app:app --bind 0.0.0.0:8080`
  - OR use Procfile (DigitalOcean will auto-detect it)

**Environment Variables:**
- `FLASK_DEBUG` = `false`
- `PORT` = `8080` (DigitalOcean sets this automatically, but you can specify)

**Resource Plan:**
- **Basic Plan:** $5/month (512MB RAM, 1GB storage) - **Recommended to start**
- **Professional Plan:** $12/month (1GB RAM, more resources)

### 4. Deploy
1. Review all settings
2. Click **"Create Resources"**
3. Wait 2-5 minutes for build
4. Your app will be live! 🎉

## 🌐 Access Your App

After deployment, DigitalOcean provides:
- **URL:** `https://your-app-name.ondigitalocean.app`
- **Custom Domain:** Can add in Settings → Domains

## 🔄 Auto-Deployments

Once connected to GitHub:
- **Push to main branch** → Auto-deploys
- **Manual deploy:** App → Deployments → Create Deployment

## 🐛 Troubleshooting

### Build Fails
- Check build logs in DigitalOcean dashboard
- Verify Python version (should be 3.11+)
- Ensure all dependencies in requirements.txt

### App Crashes on Startup
- Check runtime logs
- Verify `gunicorn` is in requirements.txt ✅ (already there)
- Check PORT environment variable

### yt-dlp Not Working
- Verify `yt-dlp==2025.12.8` in requirements.txt ✅ (already there)
- Check runtime logs for subprocess errors
- May need to install system dependencies (unlikely with Python package)

### Video Downloads Timeout
- DigitalOcean has no timeout limits (unlike Vercel)
- Check if video URL is accessible
- Verify subprocess calls work (check logs)

## 💰 Pricing

**Basic Plan ($5/month):**
- 512MB RAM
- 1GB storage
- Perfect for your app

**Professional Plan ($12/month):**
- 1GB RAM
- More storage
- Better for high traffic

## 📝 Important Notes

1. **Procfile vs Run Command:**
   - DigitalOcean will auto-detect your Procfile
   - If it doesn't, manually set run command: `gunicorn app:app --bind 0.0.0.0:8080`

2. **Port Configuration:**
   - DigitalOcean sets PORT automatically
   - Your app.py already uses `os.getenv('PORT', 5001)` ✅
   - Procfile uses `$PORT` ✅

3. **File Storage:**
   - Downloads are stored in `/tmp` (temporary)
   - Files are cleaned up automatically
   - For permanent storage, use DigitalOcean Spaces (object storage)

4. **SSL Certificate:**
   - Automatically provided by DigitalOcean
   - HTTPS enabled by default

## ✅ Your App is Ready!

Everything is configured correctly:
- ✅ Dependencies in requirements.txt
- ✅ Gunicorn for production
- ✅ Environment variable handling
- ✅ Proper port configuration

Just follow steps 1-4 above and you're good to go! 🚀

