# 🚀 Quick Deployment Reference

## 📝 Pre-Deployment Checklist

- [ ] `best_model.keras` is committed to repository
- [ ] `knowledge_db.json` is committed
- [ ] All Python files are present (app.py, preprocessing.py, etc.)
- [ ] Docker installed locally (for testing)
- [ ] GitHub repository is up to date

## 🐳 Local Docker Testing

### Quick Test (PowerShell)
```powershell
cd backend
.\docker-build.ps1
```

### Manual Build & Run
```powershell
# Build
docker build -t trimodal-xai-backend .

# Run
docker run -p 8000:8000 trimodal-xai-backend

# Test
curl http://localhost:8000/health
```

### Using Docker Compose
```powershell
docker-compose up
```

## 🌐 Deploy to Render - Step by Step

### Step 1: Push to GitHub
```powershell
git add .
git commit -m "Add Docker deployment configuration"
git push origin main
```

### Step 2: Create Render Account
- Go to https://render.com/
- Sign up with GitHub

### Step 3: Deploy Using Blueprint (Easiest)
1. Dashboard → **New +** → **Blueprint**
2. Connect **TriModalXAI** repository
3. Click **Apply**
4. Wait 5-10 minutes ☕
5. Get your URL: `https://trimodal-xai-backend.onrender.com`

### Step 4: Test Deployed API
```bash
# Health check
curl https://your-app.onrender.com/health

# Swagger docs
# Visit: https://your-app.onrender.com/docs

# Predict
curl -X POST "https://your-app.onrender.com/predict" \
  -F "file=@leaf_image.jpg"
```

## ⚡ Quick Commands

```powershell
# Build Docker image
docker build -t trimodal-xai-backend .

# Run container
docker run -p 8000:8000 trimodal-xai-backend

# Stop container
docker stop $(docker ps -q --filter ancestor=trimodal-xai-backend)

# View logs
docker logs $(docker ps -q --filter ancestor=trimodal-xai-backend)

# Clean up
docker system prune -a
```

## 🔍 Verify Deployment

**Check 1: Health Endpoint**
```bash
curl https://your-app.onrender.com/health
```
Expected: `{"status":"healthy","model_loaded":true,"knowledge_db_loaded":true}`

**Check 2: Classes Endpoint**
```bash
curl https://your-app.onrender.com/classes
```
Expected: List of 7 plant classes

**Check 3: Swagger UI**
Visit: `https://your-app.onrender.com/docs`

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "Out of memory" | Upgrade to Starter plan ($7/mo) |
| "Model not found" | Ensure `best_model.keras` is in repo |
| "Build timeout" | Model file too large - use Git LFS |
| "Cold start slow" | Normal for free tier; upgrade to paid |
| "500 error" | Check Render logs for TensorFlow errors |

## 📊 Performance Tips

- **Free Tier**: Works but slow, sleeps after 15 min
- **Starter Tier**: Recommended for ML ($7/mo)
- **Cold Start**: First request takes 30-60s
- **Warm Start**: Subsequent requests <5s

## 🔐 Production Checklist

- [ ] Update CORS origins in `app.py`
- [ ] Add API key authentication
- [ ] Enable rate limiting
- [ ] Monitor with Render metrics
- [ ] Set up custom domain (optional)

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com/
- **Community**: https://community.render.com/

---

**🎉 Your API is now deployed and ready to use!**

Base URL: `https://trimodal-xai-backend.onrender.com`
Docs: `https://trimodal-xai-backend.onrender.com/docs`
