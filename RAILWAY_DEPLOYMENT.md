# 🚂 Railway Deployment Guide - TriModal XAI Backend

## Why Railway?

✅ **Generous Free Tier**: $5/month of free credits (enough for testing)  
✅ **Native Docker Support**: Perfect for ML/AI applications  
✅ **Auto-Deploy**: Connects directly to GitHub  
✅ **Better for Python/ML**: Unlike Vercel (optimized for Node.js)  
✅ **Environment Variables**: Easy configuration  
✅ **Custom Domains**: Free SSL certificates  

---

## 📋 Prerequisites

1. ✅ GitHub account with your repo pushed
2. ✅ Railway account (free signup at https://railway.app)
3. ✅ Docker configuration files (already created!)

---

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up for Railway

1. Go to **https://railway.app**
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with your **GitHub account** (recommended)
4. Authorize Railway to access your repositories

### Step 2: Create New Project

1. Click **"New Project"** on Railway dashboard
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: **`shrinidhi0811/TriModalXAI`**
4. Railway will auto-detect the Dockerfile!

### Step 3: Configure the Deployment

Railway should automatically detect your Dockerfile, but verify these settings:

1. **Root Directory**: Leave as `/` (or set to `backend` if needed)
2. **Dockerfile Path**: Should auto-detect `backend/Dockerfile`
3. **Builder**: Docker (auto-detected)

### Step 4: Add Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
TF_ENABLE_ONEDNN_OPTS=0
ENV=production
PYTHONUNBUFFERED=1
PORT=8000
```

Railway automatically provides `$PORT` variable, but setting it helps.

### Step 5: Deploy!

1. Click **"Deploy"**
2. Watch the build logs (takes 5-10 minutes first time)
3. Railway will build your Docker image
4. Once deployed, Railway gives you a URL like: `https://trimodal-xai-backend.up.railway.app`

### Step 6: Test Your API

1. Visit: `https://your-app.up.railway.app/docs`
2. Test the `/health` endpoint
3. Try uploading a leaf image to `/predict`

---

## 📊 Monitoring & Logs

### View Logs
- Railway Dashboard → Your Service → **Deployments** → Click latest deployment
- Real-time logs show TensorFlow loading, API requests, etc.

### Check Metrics
- **Deployments** tab: CPU, Memory, Network usage
- **Metrics** tab: Historical performance data

### Health Check
Railway automatically monitors `/health` endpoint

---

## 🔄 Auto-Deploy Setup

Railway automatically sets up auto-deploy from GitHub:

1. **Push to main branch** → Automatic deployment
2. **View in Dashboard**: See deployment progress in real-time
3. **Rollback**: Easy one-click rollback to previous versions

To disable auto-deploy:
- Service Settings → **Auto Deploy** → Toggle off

---

## 💰 Free Tier Limits

Railway's **Starter Plan** (Free):
- **$5 in free credits** per month
- **500 hours** of runtime (~20 days)
- **1 GB RAM** per service (sufficient for your model!)
- **1 GB disk space**
- **100 GB bandwidth**

**Estimated Usage**:
- Your app should use ~0.5-1 GB RAM
- Free tier covers **testing and light production use**
- Upgrade to **Developer Plan ($5/mo)** for more credits

---

## 🛠️ Troubleshooting

### Build Fails

**Check Dockerfile path**:
```bash
# Should be:
backend/Dockerfile
```

**Verify Docker context**:
- Context should be `backend` directory
- All files (model, code) must be in backend/

### Memory Issues

**Out of Memory (OOM)**:
- Free tier has 1 GB RAM (should be enough)
- If crashing, check logs for `MemoryError`
- Consider upgrading to Developer plan (8 GB RAM)

### Model Not Loading

**Check logs for**:
```
FileNotFoundError: best_model.keras
```

**Solution**:
- Ensure `best_model.keras` is in `backend/` directory
- Check if file is too large for GitHub (>100 MB)
- Use Git LFS if needed:
  ```bash
  git lfs install
  git lfs track "*.keras"
  git add .gitattributes
  git add backend/best_model.keras
  git commit -m "Add model with Git LFS"
  git push
  ```

### Slow Cold Starts

Railway doesn't sleep free tier apps aggressively like Render, but:
- First request after inactivity: 5-10 seconds
- Model loading: ~15-20 seconds on startup
- Normal requests: <2 seconds

---

## 🎯 Quick Commands Reference

### Push Changes & Redeploy
```powershell
git add .
git commit -m "Update backend code"
git push origin main
# Railway auto-deploys!
```

### View Local Logs (before deploying)
```powershell
cd backend
docker build -t trimodal-test .
docker run -p 8000:8000 trimodal-test
```

### Check Git LFS Status
```powershell
git lfs ls-files
```

---

## 🌐 Custom Domain (Optional)

Railway provides free custom domains:

1. **Settings** → **Domains**
2. Click **"Generate Domain"** (free Railway subdomain)
3. Or add **custom domain** (your own domain + free SSL)

Example: `trimodal-xai.yourdomain.com`

---

## 📈 Upgrade Options

If you need more resources:

### Developer Plan - $5/month
- **$5 credits** included
- **8 GB RAM** per service
- **Metrics & Analytics**
- **Priority support**

### Team Plan - $20/month
- **$20 credits** included
- **32 GB RAM** per service
- **Team collaboration**
- **Advanced features**

---

## ✅ Deployment Checklist

Before deploying, ensure:

- [ ] All code pushed to GitHub (`main` branch)
- [ ] `backend/best_model.keras` exists and accessible
- [ ] `backend/knowledge_db.json` exists
- [ ] `backend/Dockerfile` is correct
- [ ] Model file <100 MB or using Git LFS
- [ ] Railway account created and linked to GitHub
- [ ] Environment variables configured in Railway

---

## 🎉 You're All Set!

Your FastAPI backend will be live at:
```
https://your-app-name.up.railway.app
```

**API Documentation**: `https://your-app-name.up.railway.app/docs`

**Health Check**: `https://your-app-name.up.railway.app/health`

---

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: Report issues in your repo

---

**Happy Deploying! 🚀**
