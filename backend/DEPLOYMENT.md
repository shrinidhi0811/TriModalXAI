# 🐳 Docker & Render Deployment Guide

## 📦 What's Included

- **`Dockerfile`** - Production-ready Docker image configuration
- **`docker-compose.yml`** - Local testing with Docker Compose
- **`.dockerignore`** - Excludes unnecessary files from Docker build
- **`render.yaml`** - Render blueprint for automatic deployment

## 🧪 Test Locally with Docker

### Build the Docker Image

```powershell
cd backend
docker build -t trimodal-xai-backend .
```

### Run the Container

```powershell
docker run -p 8000:8000 trimodal-xai-backend
```

### OR Use Docker Compose

```powershell
docker-compose up
```

Access the API at: http://localhost:8000/docs

### Stop the Container

```powershell
# If using docker run
docker ps  # Find container ID
docker stop <container-id>

# If using docker-compose
docker-compose down
```

## 🚀 Deploy to Render

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```powershell
   git add .
   git commit -m "Add Docker configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select `TriModalXAI` repository
   - Render will automatically detect `render.yaml`
   - Click **"Apply"**

3. **Wait for Deployment**
   - Render will build the Docker image (takes 5-10 minutes first time)
   - Once deployed, you'll get a URL like: `https://trimodal-xai-backend.onrender.com`

### Method 2: Manual Web Service Creation

1. **Go to Render Dashboard**
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository**
   - Select your `TriModalXAI` repository
   - Branch: `main`

3. **Configure Service**
   - **Name**: `trimodal-xai-backend`
   - **Region**: Oregon (or closest to you)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Instance Type**: Free (or Starter for better performance)

4. **Environment Variables**
   ```
   TF_ENABLE_ONEDNN_OPTS=0
   ENV=production
   PYTHONUNBUFFERED=1
   ```

5. **Advanced Settings**
   - Health Check Path: `/health`
   - Auto-Deploy: Yes

6. **Create Web Service**

## 🔧 Important Notes

### Free Tier Limitations

- **RAM**: 512 MB (might be tight for TensorFlow)
- **CPU**: 0.1 CPU
- **Sleep**: Spins down after 15 min of inactivity
- **Cold Start**: ~30-60 seconds to wake up

**Recommendation**: Use **Starter plan** ($7/month) for:
- 2 GB RAM (better for ML models)
- 1 CPU
- No sleep
- Faster performance

### Model File Size

Your `best_model.keras` must be in the repository. If it's too large (>100MB):

1. **Use Git LFS** (Large File Storage)
   ```powershell
   git lfs install
   git lfs track "*.keras"
   git add .gitattributes
   git add best_model.keras
   git commit -m "Add model with LFS"
   git push
   ```

2. **Or host model elsewhere** and download during startup:
   - Upload to Google Drive, S3, or Hugging Face
   - Modify `app.py` to download on startup

### Memory Optimization

If you hit memory limits on free tier:

1. **Reduce workers** in Dockerfile:
   ```dockerfile
   CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
   ```

2. **Use CPU-only TensorFlow** (already configured)

3. **Clear model from memory** after prediction if needed

## 📊 Monitoring

### Check Deployment Status

Visit Render Dashboard → Your Service → Logs

### Health Check

```bash
curl https://your-app.onrender.com/health
```

### Test API

```bash
curl -X POST "https://your-app.onrender.com/predict" \
  -F "file=@leaf_image.jpg"
```

## 🐛 Troubleshooting

### Build Fails

**Error**: "Out of memory during build"
- **Solution**: Reduce image size, use multi-stage build, or upgrade plan

**Error**: "Model file not found"
- **Solution**: Ensure `best_model.keras` is committed to repository

### Runtime Issues

**Error**: "Application startup failed"
- Check Render logs for TensorFlow errors
- Verify all dependencies are in `requirements.txt`

**Error**: "Out of memory"
- Upgrade to Starter plan (2 GB RAM)
- Optimize model loading

**Error**: "Connection timeout"
- Increase health check timeout
- Model loading takes time on first request

### Cold Starts (Free Tier)

To keep service warm:
- Use a cron job to ping every 10 minutes
- Upgrade to paid plan (no sleep)

## 🔐 Security (Production)

1. **Add CORS Origins** in `app.py`:
   ```python
   allow_origins=["https://your-frontend.com"]
   ```

2. **Add API Key Authentication**:
   ```python
   from fastapi import Header, HTTPException
   
   @app.post("/predict")
   async def predict(
       file: UploadFile,
       api_key: str = Header(None)
   ):
       if api_key != os.getenv("API_KEY"):
           raise HTTPException(401, "Invalid API key")
   ```

3. **Rate Limiting**:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/predict")
   @limiter.limit("10/minute")
   async def predict(...):
       ...
   ```

## 📈 Scaling

### Horizontal Scaling
- Add more instances in Render
- Use load balancer

### Vertical Scaling
- Upgrade to higher plan
- More RAM/CPU

### Caching
- Cache model in memory (already done)
- Cache preprocessed images
- Use Redis for results caching

## 💰 Cost Estimates

| Plan | Price | RAM | CPU | Features |
|------|-------|-----|-----|----------|
| Free | $0 | 512 MB | 0.1 | 750 hrs/month, sleeps |
| Starter | $7/mo | 2 GB | 1 | No sleep, better performance |
| Standard | $25/mo | 4 GB | 2 | Production-ready |

**Recommendation**: Start with **Starter** for ML workloads.

## 🎉 Success!

Once deployed, your API will be live at:
```
https://trimodal-xai-backend.onrender.com
```

Test it:
- Docs: `https://your-url.onrender.com/docs`
- Health: `https://your-url.onrender.com/health`
- Predict: POST to `https://your-url.onrender.com/predict`

---

## 📞 Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [Docker Documentation](https://docs.docker.com/)
