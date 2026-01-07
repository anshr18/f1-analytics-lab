# Quick Vercel Deployment Guide

Get your F1 Intelligence Hub live in minutes!

## 🚀 Step 1: Deploy Backend (Choose One)

### Railway (Easiest - Recommended)

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will detect the monorepo. Choose **"apps/api"** as root
5. Add these services to your project:
   - **PostgreSQL** (Database)
   - **Redis** (Cache)
6. Set environment variables (copy from `apps/api/.env.example`):
   ```
   DATABASE_URL=<Railway will auto-fill this>
   REDIS_URL=<Railway will auto-fill this>
   CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
   SECRET_KEY=<generate a random string>
   ```
7. Deploy! Railway will give you a URL like: `https://f1hub-api.up.railway.app`

**Cost**: ~$5/month (free tier available)

### Alternative: Render

1. Go to [render.com](https://render.com) and sign in
2. **New** → **Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Root Directory**: `apps/api`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn f1hub.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL & Redis from Render dashboard
6. Set environment variables
7. Deploy! You'll get: `https://f1hub-api.onrender.com`

**Cost**: ~$7/month (free tier available with cold starts)

## 🌐 Step 2: Deploy Frontend to Vercel

### Option A: Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New"** → **"Project"**
3. Import your repository
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `apps/web` ⚠️ Important!
   - **Build Command**: `npm run build` (default, should auto-fill)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)
5. Add Environment Variables:
   - Click **"Environment Variables"**
   - Add variable:
     - **Name**: `NEXT_PUBLIC_API_URL`
     - **Value**: Your backend URL from Step 1 (e.g., `https://f1hub-api.up.railway.app`)
     - **Environment**: Production, Preview, Development (check all)
6. Click **"Deploy"**
7. ✅ Done! Your app will be live at `https://your-project.vercel.app`

### Option B: Vercel CLI (For Developers)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy (from project root)
vercel

# Follow prompts, set root directory to: apps/web
```

## 🔧 Step 3: Configure CORS

Update your backend's `CORS_ORIGINS` environment variable to include your Vercel URL:

**Railway/Render:**
```
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

This allows your frontend to communicate with your backend.

## ✅ Step 4: Test Your Deployment

1. Visit your Vercel URL
2. Try navigating between pages
3. Test the Dashboard page (should load race data)
4. Check browser console for errors (F12)

## 🎯 Troubleshooting

### "Failed to fetch" errors
- ✅ Check `NEXT_PUBLIC_API_URL` is set in Vercel
- ✅ Verify backend CORS includes your Vercel domain
- ✅ Ensure backend is running and accessible

### Build fails on Vercel
- ✅ Verify **Root Directory** is set to `apps/web`
- ✅ Check build logs in Vercel dashboard
- ✅ Test build locally: `cd apps/web && npm run build`

### API returns 404
- ✅ Ensure backend is deployed and running
- ✅ Check API URL doesn't have trailing slash
- ✅ Verify API endpoint paths in code

## 📊 What You Get

**Free Tier Limits:**
- **Vercel**: 100 GB bandwidth/month, unlimited deployments
- **Railway**: $5 free credit/month
- **Render**: Free tier with cold starts (spins down after inactivity)

**Recommended for Production:**
- **Vercel Pro**: $20/month (1TB bandwidth, analytics)
- **Railway Pro**: ~$10-20/month (better resources)
- **Total**: ~$30-40/month for production-ready setup

## 🚀 Next Steps

1. ✅ Set up custom domain in Vercel
2. ✅ Enable Vercel Analytics
3. ✅ Set up preview deployments (automatic with GitHub)
4. ✅ Configure production database backups
5. ✅ Add monitoring (Sentry, LogRocket, etc.)

## 📝 Important Notes

- **Environment Variables**: Always add them in Vercel dashboard, not in code
- **Auto-Deploy**: Commits to `main` branch auto-deploy to production
- **Preview URLs**: Each PR gets its own preview deployment
- **Build Time**: First deployment ~5-10 minutes, subsequent builds ~2-3 minutes

## 🆘 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: [Report issues here](https://github.com/your-username/f1-intelligence-hub/issues)

---

**Deployment Time**: ~15-30 minutes total (backend + frontend)

Happy deploying! 🏎️💨
