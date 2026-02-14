# 🚀 Deploying Spendy to Render via GitHub

## What's been added for deployment
- `Procfile` — tells Render how to start the app (via Gunicorn)
- `render.yaml` — one-click Render config (auto-generates a secret key)
- `gunicorn` added to `requirements.txt`
- `app.py` updated to use `SECRET_KEY` environment variable
- `DATA_FILE` set to `/tmp/user_data.json` (writable on Render)
- `.gitignore` added

> ⚠️ **Note on data persistence:** Render's free tier uses an ephemeral filesystem, meaning `user_data.json` resets on each deploy/restart. For persistent data, you'd need to add a database (e.g. Render's free PostgreSQL). The app works fine for demos as-is.

---

## Step 1 — Push to GitHub

### If you don't have Git installed:
Download from https://git-scm.com

### Create a new GitHub repo:
1. Go to https://github.com/new
2. Name it `spendy` (or anything you like)
3. Leave it **empty** (no README, no .gitignore)
4. Click **Create repository**

### Push your code:
Open a terminal in this project folder and run:

```bash
git init
git add .
git commit -m "Initial commit — Spendy ready for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/spendy.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 2 — Deploy on Render

### Option A — One-click via render.yaml (easiest)
1. Go to https://render.com and sign up / log in
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account if prompted
4. Select your `spendy` repository
5. Render will detect `render.yaml` and configure everything automatically
6. Click **"Apply"** — your app deploys in ~2 minutes!

### Option B — Manual setup
1. Go to https://render.com → **"New +"** → **"Web Service"**
2. Connect your GitHub repo
3. Fill in the settings:
   - **Name:** spendy
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Under **Environment Variables**, add:
   - `SECRET_KEY` → click "Generate" for a random value
5. Click **"Create Web Service"**

---

## Step 3 — Your app is live!

Render will give you a URL like:
```
https://spendy.onrender.com
```

Every time you push to GitHub, Render auto-deploys the update.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| App crashes on start | Check Render logs → likely a missing dependency |
| Static files not loading | Make sure `static/` folder is committed to GitHub |
| Data resets on restart | Expected on free tier — use a DB for persistence |
| Slow first load | Free tier "spins down" after inactivity — first visit takes ~30s |

---

## Optional: Add a custom domain
In Render dashboard → your service → **Settings** → **Custom Domains**
