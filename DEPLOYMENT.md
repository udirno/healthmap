# HealthMap Deployment Guide

Deploy HealthMap: frontend to **Vercel**, backend to **Render**.

**Repository:** https://github.com/udirno/healthmap.git

## Prerequisites

- GitHub account with the repo pushed
- [Vercel account](https://vercel.com) (free tier)
- [Render account](https://render.com) (free tier)
- API keys: Anthropic, OpenWeather, Mapbox

---

## Step 1: Deploy Backend to Render

### Option A: Blueprint (Recommended)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account and select **`udirno/healthmap`**
4. Render detects `render.yaml` and shows 3 services: `healthmap-api`, `healthmap-db`, `healthmap-redis`
5. Set the environment variables when prompted:
   - `ANTHROPIC_API_KEY` — your Anthropic key
   - `OPENWEATHER_API_KEY` — your OpenWeather key
   - `CORS_ORIGINS` — leave blank for now (update after Vercel deploy)
6. Click **"Apply"** — wait 5-10 minutes for first deploy
7. Note your backend URL (e.g., `https://healthmap-api.onrender.com`)
8. Verify: visit `https://healthmap-api.onrender.com/health` → should return `{"status": "healthy"}`

### Option B: Manual Setup

1. **Create PostgreSQL**: New+ → PostgreSQL → name: `healthmap-db`, plan: Free
2. **Create Redis**: New+ → Redis → name: `healthmap-redis`, plan: Free
3. **Create Web Service**: New+ → Web Service → connect `udirno/healthmap`
   - Name: `healthmap-api`
   - Branch: `main`
   - Runtime: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free
4. Add environment variables:
   - `DATABASE_URL` — connection string from PostgreSQL
   - `REDIS_URL` — connection string from Redis
   - `ANTHROPIC_API_KEY` — your key
   - `OPENWEATHER_API_KEY` — your key
   - `CORS_ORIGINS` — your Vercel URL (after Step 2)
   - `DEBUG` — `false`

---

## Step 2: Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"** and select **`udirno/healthmap`**
3. Configure the project:
   - **Root Directory**: Click "Edit" and set to **`frontend`** (critical!)
   - Framework Preset: Next.js (auto-detected)
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
4. Add environment variables:
   - `NEXT_PUBLIC_MAPBOX_TOKEN` — your Mapbox token (from `frontend/.env.local`)
   - `NEXT_PUBLIC_API_URL` — your Render backend URL (e.g., `https://healthmap-api.onrender.com`)
5. Click **"Deploy"** — wait 2-3 minutes
6. Note your frontend URL (e.g., `https://healthmap.vercel.app`)

---

## Step 3: Connect Frontend ↔ Backend

1. Go to Render dashboard → `healthmap-api` service → **Environment** tab
2. Set `CORS_ORIGINS` to your Vercel URL:
   ```
   https://healthmap.vercel.app
   ```
3. Save — this triggers a redeploy

---

## Step 4: Seed the Database

Tables are created automatically on app startup. To populate sample disease data, run:

```bash
curl -X POST https://healthmap-api.onrender.com/api/seed
```

This populates 20 countries with daily COVID-19 records for 2022 plus climate data. Safe to call multiple times (checks if already seeded).

---

## Environment Variables Summary

### Backend (Render)
| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Auto-set by Render (Blueprint) |
| `REDIS_URL` | Auto-set by Render (Blueprint) |
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `OPENWEATHER_API_KEY` | Your OpenWeather key |
| `CORS_ORIGINS` | Your Vercel URL |
| `DEBUG` | `false` |

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Your Mapbox token |
| `NEXT_PUBLIC_API_URL` | Your Render backend URL |

---

## Verify Deployment

1. **Backend**: `https://healthmap-api.onrender.com/health` → `{"status": "healthy"}`
2. **Frontend**: Visit your Vercel URL → map loads, metrics display
3. **AI Chat**: Ask a question → Claude responds with formatted insights

---

## Free Tier Limitations

- **Render**: Services sleep after 15 min of inactivity. First request after sleep takes ~30s to cold-start.
- **PostgreSQL**: 90-day expiration on free tier (recreate or upgrade before expiry).
- **Redis**: 25MB max memory.
- **Vercel**: Hobby plan, no commercial use.

---

## Continuous Deployment

Both platforms auto-deploy on push to `main`:
- **Vercel**: Automatic on every push
- **Render**: Automatic if enabled in service settings

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS errors | Ensure `CORS_ORIGINS` on Render matches your exact Vercel URL |
| Map not loading | Check `NEXT_PUBLIC_MAPBOX_TOKEN` is set in Vercel |
| API errors in browser | Check `NEXT_PUBLIC_API_URL` points to your Render URL |
| Module not found on Vercel | Verify Root Directory is set to `frontend` |
| Backend 502 errors | Check Render logs; ensure `$PORT` is used in start command |
| Slow first load | Normal on free tier — Render cold-starts after 15min idle |
