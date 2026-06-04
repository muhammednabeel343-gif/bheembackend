# Image URL Rendering - Debugging Guide

## Quick Test Steps

### 1. Check Backend Configuration

```bash
# Test locally
curl http://localhost:8000/debug/config

# Expected output:
{
  "api_base_url": "http://localhost:8000",
  "cors_origins_list": ["http://localhost:5173"],
  "upload_dir": "/path/to/backend/uploads",
  "upload_dir_exists": true
}
```

### 2. Test Image URL Normalization

```bash
# Test with localhost URL (from old database)
curl "http://localhost:8000/debug/test-image-url?url=http://127.0.0.1:8000/uploads/abc123.jpg"

# Expected:
{
  "input": "http://127.0.0.1:8000/uploads/abc123.jpg",
  "normalized": "http://localhost:8000/uploads/abc123.jpg",
  "api_base_url": "http://localhost:8000"
}

# Test with relative path
curl "http://localhost:8000/debug/test-image-url?url=/uploads/abc123.jpg"

# Expected:
{
  "input": "/uploads/abc123.jpg",
  "normalized": "http://localhost:8000/uploads/abc123.jpg",
  "api_base_url": "http://localhost:8000"
}
```

### 3. Check Actual Game Image URLs

```bash
# Get a game with token
curl http://localhost:8000/games/1 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check the image_url field - it should be normalized
# Example response:
{
  "id": 1,
  "name": "Game Name",
  "image_url": "http://localhost:8000/uploads/abc123.jpg",  # Should be correct
  ...
}
```

### 4. Test Image File Exists

```bash
# Check if actual image file exists
ls -la backend/uploads/

# Or on Windows
dir backend\uploads\

# You should see files like: abc123.jpg, def456.png, etc.
```

### 5. Test Direct Image Access

```bash
# Try accessing image directly
curl http://localhost:8000/uploads/abc123.jpg -v

# Should return 200 with image data (or 404 if file doesn't exist)
```

---

## Common Issues & Solutions

### Issue 1: API_BASE_URL is NULL in debug

**Problem:**
```json
{
  "api_base_url": null,
  "cors_origins_list": ["http://localhost:5173"]
}
```

**Solution:**
- Set `API_BASE_URL` in `.env`:
  ```
  API_BASE_URL=http://localhost:8000
  ```
- For Railway, set in Variables:
  ```
  API_BASE_URL=https://your-railway-app.up.railway.app
  ```

### Issue 2: Image File Not Found (404)

**Problem:** Frontend shows broken image icon

**Solutions:**
1. **Check file exists:**
   ```bash
   ls backend/uploads/abc123.jpg
   ```

2. **Check upload directory permissions:**
   ```bash
   # Make sure directory is writable
   chmod 755 backend/uploads/
   ```

3. **Check UPLOAD_DIR path is correct:**
   ```bash
   curl http://localhost:8000/debug/config | grep upload_dir
   ```

### Issue 3: CORS Error Blocking Images

**Problem:** Browser console shows CORS error

**Solution:**
- In Railway, set `CORS_ORIGINS`:
  ```
  CORS_ORIGINS=https://your-frontend.vercel.app
  ```

### Issue 4: Images Show Wrong URL Format

**Problem:** URL is still like `http://127.0.0.1:8000/uploads/...` in production

**Solution:**
1. Verify `API_BASE_URL` is set in Railway:
   ```
   API_BASE_URL=https://your-railway-app.up.railway.app
   ```

2. Verify frontend is calling the right endpoints:
   - `GET /games` - should return normalized URLs
   - `GET /games/{id}` - should return normalized URLs

---

## Step-by-Step Fix Process

### For Development

```bash
cd backend

# 1. Update .env
echo "API_BASE_URL=http://localhost:8000" >> .env

# 2. Restart backend
python -m uvicorn app.main:app --reload

# 3. Test debug endpoints (see above)
# 4. Check browser developer tools for actual image URLs
```

### For Railway Production

```bash
# 1. In Railway dashboard, add/verify variables:
# DATABASE_URL = (auto)
# SECRET_KEY = your-key
# API_BASE_URL = https://your-railway-app.up.railway.app  # CRITICAL!
# CORS_ORIGINS = https://your-frontend.vercel.app

# 2. Trigger redeploy by pushing changes
git add app/utils/image_url.py
git commit -m "Improve image URL normalization"
git push origin main

# 3. After deploy, test:
# curl https://your-app.railway.app/debug/config
# curl "https://your-app.railway.app/debug/test-image-url?url=http://127.0.0.1:8000/uploads/test.jpg"
```

---

## Browser Developer Tools Check

### In Frontend (Chrome DevTools)

1. **Right-click image → Inspect**
2. Look at the `<img src="...">` attribute
3. Check what URL is being loaded:
   - ✅ Correct: `http://localhost:8000/uploads/abc.jpg`
   - ❌ Wrong: `http://127.0.0.1:8000/uploads/abc.jpg`
   - ❌ Wrong: `undefined/uploads/abc.jpg`

4. **Network tab:**
   - Click on the image request
   - Check Status (should be 200)
   - Check URL (should match the one in src attribute)
   - Check Response (should show image data)

---

## Database Debug

If images still show wrong data after all fixes:

```python
# Run this Python script in backend directory
from app.database import SessionLocal
from app.models.game import Game

db = SessionLocal()
games = db.query(Game).all()

for game in games:
    print(f"Game: {game.name}")
    print(f"  image_url: {game.image_url}")
    print(f"  thumbnail_url: {game.thumbnail_url}")
    print()
```

---

## Environment Variables Checklist

### Local Development (.env)
```
✅ DATABASE_URL=postgresql://...
✅ SECRET_KEY=your-key
✅ API_BASE_URL=http://localhost:8000
✅ CORS_ORIGINS=http://localhost:5173
```

### Railway (Dashboard Variables)
```
✅ DATABASE_URL = (auto from Postgres plugin)
✅ SECRET_KEY = your-production-key
✅ API_BASE_URL = https://your-railway-app.up.railway.app  (CRITICAL!)
✅ CORS_ORIGINS = https://your-vercel-frontend.app
```

### Frontend .env
```
✅ VITE_API_BASE_URL=http://localhost:8000  (local)
   or
✅ VITE_API_BASE_URL=https://your-railway-app.up.railway.app  (production)
```

---

## After Making Changes

```bash
# 1. Test locally
python -m uvicorn app.main:app --reload

# 2. Verify debug endpoints work
curl http://localhost:8000/debug/config

# 3. Get a game and verify image_url is correct
curl http://localhost:8000/games/1 -H "Authorization: Bearer TOKEN"

# 4. Commit and deploy
git add app/
git commit -m "Fix image URL rendering"
git push origin main

# 5. After Railway redeploy, test production
curl https://your-app.railway.app/debug/config
curl https://your-app.railway.app/games/1 -H "Authorization: Bearer TOKEN"
```

---

## Still Having Issues?

Share the output of:
```bash
curl http://localhost:8000/debug/config
curl "http://localhost:8000/debug/test-image-url?url=http://127.0.0.1:8000/uploads/test.jpg"
curl http://localhost:8000/games/1 -H "Authorization: Bearer TOKEN" | grep image_url
```

This will help diagnose the exact problem!
