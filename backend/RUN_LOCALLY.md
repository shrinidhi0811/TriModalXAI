# 🚀 Running TriModal XAI Backend Locally

## Quick Start (Recommended)

### Using the PowerShell Script

```powershell
cd C:\Users\SHRINIDHI\Desktop\TriModalXAI\backend
.\run_local.ps1
```

This script will:
1. ✅ Create a virtual environment (if not exists)
2. ✅ Install all dependencies automatically
3. ✅ Start the FastAPI server with auto-reload

---

## Manual Setup (Step-by-Step)

### Step 1: Navigate to Backend Directory

```powershell
cd C:\Users\SHRINIDHI\Desktop\TriModalXAI\backend
```

### Step 2: Create Virtual Environment (Optional but Recommended)

```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
.\venv\Scripts\activate.bat
```

### Step 4: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This will install ~2GB of packages including TensorFlow, OpenCV, etc. First install takes 5-10 minutes.

### Step 5: Start the Server

```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Options:**
- `--reload`: Auto-restart on code changes (for development)
- `--host 0.0.0.0`: Accept connections from any IP
- `--port 8000`: Run on port 8000

---

## Testing the API

### 1. Open API Documentation (Swagger UI)

Visit: **http://localhost:8000/docs**

This interactive UI lets you:
- See all available endpoints
- Test API calls directly in the browser
- View request/response schemas

### 2. Health Check

**Browser:**
```
http://localhost:8000/health
```

**PowerShell:**
```powershell
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "model_loaded": false,
  "knowledge_db_loaded": false,
  "details": {
    "model": "not_loaded",
    "knowledge_db": "not_loaded"
  }
}
```

### 3. Test Prediction

**Using Swagger UI** (Easiest):
1. Go to http://localhost:8000/docs
2. Click on `/predict` endpoint
3. Click "Try it out"
4. Upload a leaf image
5. Click "Execute"

**Using PowerShell:**
```powershell
curl -X POST "http://localhost:8000/predict" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@path\to\your\leaf_image.jpg"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/predict"
files = {"file": open("leaf_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

---

## Server Output

When the server starts, you'll see:

```
🚀 Starting TriModal XAI Backend (Lazy Loading Mode)...
📂 Base directory: C:\Users\SHRINIDHI\Desktop\TriModalXAI\backend
🤖 Model path: C:\Users\SHRINIDHI\Desktop\TriModalXAI\backend\best_model.keras
📚 Knowledge DB path: C:\Users\SHRINIDHI\Desktop\TriModalXAI\backend\knowledge_db.json
✅ Model file exists (33.05 MB)
✅ Knowledge DB exists (7.45 KB)
🎉 Backend ready! Models will load on first request.

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Troubleshooting

### ❌ "Python not found"

**Solution:** Install Python 3.11:
```
https://www.python.org/downloads/
```

### ❌ "ModuleNotFoundError: No module named 'X'"

**Solution:** Install dependencies:
```powershell
pip install -r requirements.txt
```

### ❌ "Port 8000 already in use"

**Solution 1:** Kill the process using port 8000:
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Solution 2:** Use a different port:
```powershell
uvicorn app:app --reload --port 8001
```

### ❌ "Model file not found"

**Solution:** Ensure `best_model.keras` is in the `backend/` directory:
```powershell
ls backend\best_model.keras
```

### ❌ Server crashes on first prediction

**Cause:** Out of memory (model too large)

**Solution:** Close other applications to free up RAM, or upgrade your system RAM.

---

## Development Tips

### Auto-Reload on Code Changes

Using `--reload` flag automatically restarts the server when you edit Python files:

```powershell
uvicorn app:app --reload --port 8000
```

### View Logs in Real-Time

All print statements and logs appear in the terminal where you ran the server.

### Test Different Images

The API accepts:
- ✅ JPG/JPEG
- ✅ PNG
- ✅ Any image format supported by PIL

Image requirements:
- Any size (will be resized to 224x224 automatically)
- Color images preferred
- Clear leaf images work best

---

## Stopping the Server

Press **Ctrl+C** in the terminal where the server is running.

---

## Next Steps

1. ✅ **Test locally** - Make sure everything works
2. ✅ **Build frontend** - Connect a React/HTML frontend
3. ✅ **Deploy to cloud** - Use Railway/Render when ready

---

## Quick Commands Reference

```powershell
# Navigate to backend
cd C:\Users\SHRINIDHI\Desktop\TriModalXAI\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app:app --reload --port 8000

# Run script (all-in-one)
.\run_local.ps1
```

---

**Happy developing! 🎉**
