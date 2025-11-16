# Quick Deployment Guide

This guide will help you deploy your AI Genealogy Platform in under 10 minutes with NO coding required!

## 🚀 Fastest Option: Railway.app (Recommended)

Railway is the easiest way to deploy this application. It's literally 4 clicks!

### Step-by-Step:

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Click "Login with GitHub"
   - Authorize Railway to access your GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `geneaology` repository
   - Click "Deploy Now"

3. **Wait for Build** (2-3 minutes)
   - Railway automatically detects it's a Flask app
   - Installs all dependencies
   - Sets up the environment

4. **Get Your URL**
   - Click "Generate Domain"
   - Your app is live at `https://your-app.up.railway.app`
   - Share this URL with your team!

### Railway Features:
- ✅ Automatic HTTPS
- ✅ Free tier: 500 hours/month
- ✅ Auto-deploys on git push
- ✅ Easy database upgrades available
- ✅ Custom domains supported

**Cost**: Free for small projects, ~$5-10/month for medium use

---

## 🎨 Alternative Option: Render.com

Render is another great option with a generous free tier.

### Step-by-Step:

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render detects `render.yaml` automatically

3. **Configure (if needed)**
   - Name: `ai-genealogy-platform`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - Your app is live at `https://your-app.onrender.com`

### Render Features:
- ✅ Free tier (with sleep mode after inactivity)
- ✅ Paid tier: $7/month (always-on)
- ✅ PostgreSQL database available
- ✅ Auto SSL certificates

---

## 🐍 Option for Python Fans: PythonAnywhere

Perfect if you want a Python-specific platform.

### Step-by-Step:

1. **Create Account**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Create free account

2. **Upload Code**
   - Go to "Files" tab
   - Click "Upload a file" or use "Open Bash console" to git clone
   ```bash
   git clone https://github.com/yourusername/geneaology.git
   ```

3. **Create Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask"
   - Python version: 3.11
   - Path to Flask app: `/home/yourusername/geneaology/app.py`

4. **Install Dependencies**
   - Open a Bash console
   ```bash
   cd geneaology
   pip3.11 install --user -r requirements.txt
   ```

5. **Reload**
   - Go to Web tab
   - Click "Reload"
   - Visit `https://yourusername.pythonanywhere.com`

**Cost**: Free tier available, $5/month for paid

---

## 📦 For Advanced Users: Google Cloud Run

Best for auto-scaling and pay-per-use pricing.

### Step-by-Step:

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD gunicorn app:app --bind 0.0.0.0:$PORT
   ```

2. **Install Google Cloud CLI**
   - Download from [cloud.google.com/sdk](https://cloud.google.com/sdk)
   - Run `gcloud init`

3. **Deploy**
   ```bash
   gcloud run deploy ai-genealogy \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

4. **Get URL**
   - Cloud Run provides a URL like `https://ai-genealogy-xxx.run.app`

**Cost**: Pay per request, free tier includes 2M requests/month

---

## 🔧 Environment Configuration

After deployment, you may want to set these environment variables:

| Variable | Value | Required? |
|----------|-------|-----------|
| `PORT` | Auto-set by platform | ✅ Yes (auto) |
| `FLASK_ENV` | `production` | ⚠️ Recommended |
| `FLASK_DEBUG` | `False` | ⚠️ Recommended |

### How to Set Env Variables:

**Railway:**
- Go to project → Variables tab
- Add variable → Save

**Render:**
- Go to service → Environment tab
- Add environment variable → Save

**PythonAnywhere:**
- Not needed for basic setup

---

## 🗄️ Database Considerations

### Current Setup (SQLite):
- ✅ Perfect for: 1-10 users, <1000 properties
- ✅ No configuration needed
- ⚠️ File-based (may reset on some platforms)

### Upgrade to PostgreSQL (for production):

**Railway:**
1. Click "New" → "Database" → "PostgreSQL"
2. Copy connection string
3. Update app to use PostgreSQL instead of SQLite

**Render:**
1. Create new "PostgreSQL" database
2. Copy internal connection string
3. Link to your web service

---

## ✅ Post-Deployment Checklist

After deploying, verify these work:

1. **Homepage Loads**
   - Visit your URL
   - Should see the AI Genealogy Platform dashboard

2. **Upload CSV**
   - Go to "Upload Data" tab
   - Upload a test CSV file
   - Verify data appears in "Properties" tab

3. **Research Function**
   - Go to "Research" tab
   - Search for a name (e.g., "John Smith")
   - Should see results from multiple sources

4. **Analytics**
   - Dashboard should show stats
   - Numbers should update after uploading data

---

## 🆘 Troubleshooting

### App won't start:
- **Check logs** in your platform's dashboard
- Common issue: Missing `requirements.txt`
- Solution: Make sure all files are committed to GitHub

### Database errors:
- **SQLite locked**: Restart the app
- **Permissions**: Check file permissions in platform settings

### Slow performance:
- **Free tiers sleep**: Upgrade to paid tier
- **Too much data**: Consider PostgreSQL upgrade

### 502/503 Errors:
- **App crashed**: Check logs for Python errors
- **Timeout**: Increase timeout in platform settings

---

## 🎯 Recommended Deployment Strategy

For most users, we recommend:

1. **Start with Railway** (easiest, best UX)
2. **Test with sample data** (10-20 properties)
3. **Monitor usage** (check Railway dashboard)
4. **Upgrade if needed** (when you hit limits)

### When to Upgrade:
- 📊 More than 100 properties → Paid tier
- 👥 More than 5 concurrent users → Paid tier
- 🗄️ Heavy research usage → PostgreSQL
- 🚀 Critical business use → Paid tier with monitoring

---

## 💡 Pro Tips

1. **Custom Domain**: Connect your own domain in Railway/Render settings
2. **Auto-Deploy**: Every git push automatically deploys (Railway/Render)
3. **Monitoring**: Use platform's built-in monitoring dashboards
4. **Backups**: Download your `genealogy.db` regularly via platform's file browser
5. **Security**: Add authentication if handling sensitive data

---

## 📞 Need Help?

If you run into issues:
1. Check the main [README.md](README.md) for detailed docs
2. Review platform-specific documentation
3. Create an issue on GitHub
4. Check platform's Discord/support channels

---

**Remember**: The hardest part is making the decision to deploy. The actual deployment is just 4 clicks! 🚀
