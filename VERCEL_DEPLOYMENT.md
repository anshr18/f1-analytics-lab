# Vercel Deployment Guide

This guide explains how to deploy the F1 Intelligence Hub frontend to Vercel.

## Important Notes

⚠️ **Backend Deployment**: The FastAPI backend (`apps/api`) **cannot** be deployed to Vercel as Vercel is optimized for frontend/serverless functions. The backend needs to be deployed separately (see Backend Deployment Options below).

This guide covers deploying only the **Next.js frontend** (`apps/web`) to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Your backend API deployed and accessible (see Backend Deployment Options)
3. GitHub repository (recommended for automatic deployments)

## Deployment Steps

### 1. Prepare Your Repository

Ensure you're on the `dev` or `main` branch with all changes committed:

```bash
git checkout dev
git status  # Should show "nothing to commit, working tree clean"
```

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel CLI (Recommended for first-time setup)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy from the project root:
```bash
vercel
```

4. Follow the prompts:
   - **Set up and deploy**: Yes
   - **Which scope**: Select your account/team
   - **Link to existing project**: No (first time)
   - **Project name**: f1-intelligence-hub (or your preferred name)
   - **In which directory is your code located**: `./apps/web`
   - **Want to override settings**: Yes
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Development Command**: `npm run dev`

#### Option B: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your Git repository
3. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

### 3. Configure Environment Variables

Add the following environment variable in your Vercel project settings:

**Production:**
- `NEXT_PUBLIC_API_URL` = Your backend API URL (e.g., `https://your-api-domain.com`)

**Preview/Development:**
- `NEXT_PUBLIC_API_URL` = Your staging/dev backend API URL

To add environment variables:
1. Go to your project in Vercel Dashboard
2. Click **Settings** → **Environment Variables**
3. Add the variable for each environment (Production, Preview, Development)

### 4. Deploy

- **First deployment**: Run `vercel` (will deploy to preview)
- **Production deployment**: Run `vercel --prod`

For GitHub-connected projects:
- Pushing to `main` branch → Production deployment
- Pushing to other branches → Preview deployment

## Backend Deployment Options

Since Vercel cannot host the FastAPI backend, choose one of these options:

### Option 1: Railway (Recommended - Easy & Fast)

Railway offers excellent Python/FastAPI support with PostgreSQL, Redis, and MinIO.

1. Go to https://railway.app
2. Create a new project
3. Deploy from your GitHub repository
4. Add services:
   - **Python app** (FastAPI from `apps/api`)
   - **PostgreSQL** database
   - **Redis** for caching/Celery
   - **MinIO** (or use Railway's S3-compatible storage)
5. Set environment variables (from `apps/api/.env.example`)
6. Railway will provide a public URL for your API

**Estimated cost**: ~$5-20/month depending on usage

### Option 2: Render

1. Go to https://render.com
2. Create a new **Web Service**
3. Connect your repository
4. Configure:
   - **Root Directory**: `apps/api`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn f1hub.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL, Redis services
6. Set environment variables

**Estimated cost**: ~$7-25/month

### Option 3: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Create app: `fly launch` (from `apps/api` directory)
4. Add Postgres: `fly postgres create`
5. Add Redis: `fly redis create`
6. Deploy: `fly deploy`

**Estimated cost**: ~$5-15/month

### Option 4: DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Create a new app from GitHub
3. Configure Python component (FastAPI)
4. Add managed databases (PostgreSQL, Redis)
5. Deploy

**Estimated cost**: ~$12-25/month

### Option 5: Self-Hosted (VPS)

Deploy to a VPS like DigitalOcean Droplet, Linode, or AWS EC2:

1. Use Docker Compose (already configured in the repo)
2. Set up reverse proxy (Nginx)
3. Configure SSL certificates (Let's Encrypt)
4. Run `docker-compose up -d`

**Estimated cost**: ~$6-40/month depending on resources

## Complete Architecture

```
┌─────────────────┐
│  Vercel         │
│  (Next.js App)  │
│  Port: 443      │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐      ┌──────────────┐
│  Railway/Render │◄────►│ PostgreSQL   │
│  (FastAPI API)  │      │ (Database)   │
│  Port: 8000     │      └──────────────┘
└────────┬────────┘
         │
         ├─────►┌──────────────┐
         │      │ Redis        │
         │      │ (Cache)      │
         │      └──────────────┘
         │
         └─────►┌──────────────┐
                │ MinIO/S3     │
                │ (Storage)    │
                └──────────────┘
```

## Testing the Deployment

Once deployed:

1. Visit your Vercel URL (e.g., `https://your-app.vercel.app`)
2. Check that the app loads correctly
3. Verify API connection by checking any data-fetching page
4. Test navigation between pages
5. Check browser console for any errors

## Troubleshooting

### Build Fails

- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify TypeScript errors: `npm run type-check`

### API Connection Issues

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in your FastAPI backend
- Ensure backend is accessible from Vercel's regions

### Environment Variables Not Working

- Environment variables must start with `NEXT_PUBLIC_` to be accessible in the browser
- Redeploy after adding new environment variables
- Check variable spelling and casing

## CORS Configuration for Backend

Your FastAPI backend needs to allow requests from Vercel. Update `apps/api/src/f1hub/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Add your Vercel domain
origins = [
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel domain
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Continuous Deployment

Once connected to GitHub:

1. Push to `main` branch → Automatic production deployment
2. Push to any other branch → Automatic preview deployment
3. Pull requests → Automatic preview deployment with unique URL

## Monitoring & Analytics

Vercel provides built-in:
- **Analytics**: Page views, performance metrics
- **Logs**: Function logs, build logs
- **Speed Insights**: Core Web Vitals monitoring

Access these in your Vercel project dashboard.

## Costs

**Vercel:**
- **Hobby Plan**: Free for personal projects
  - 100 GB bandwidth/month
  - Unlimited deployments
  - Custom domains

- **Pro Plan**: $20/month
  - 1 TB bandwidth/month
  - Team features
  - Priority support

**Backend Hosting:**
- See Backend Deployment Options above (~$5-40/month depending on provider)

**Total estimated monthly cost**: $0-60 depending on tier and usage

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Deploy backend to Railway/Render/other
3. ✅ Configure environment variables
4. ✅ Set up custom domain (optional)
5. ✅ Enable analytics and monitoring
6. ⬜ Set up CI/CD for automated testing
7. ⬜ Configure staging environment

## Support

For issues:
- Vercel: https://vercel.com/support
- Railway: https://docs.railway.app
- Render: https://render.com/docs

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
