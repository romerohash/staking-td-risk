# Railway Deployment Guide for Staking TD Demo (Single Service)

This guide provides step-by-step instructions for deploying the Staking Tracking Error Demo application to Railway.app as a single service, reducing latency between frontend and backend.

## Prerequisites

- A Railway account (sign up at [railway.app](https://railway.app))
- Git repository with your code pushed to GitHub/GitLab/Bitbucket
- Railway CLI (optional, for local deployment)

## Architecture Overview

The application is deployed as a single service that:
- Serves the React frontend as static files
- Provides the FastAPI backend API at `/api/*` endpoints
- Eliminates cross-service communication latency
- Simplifies deployment and configuration

## Deployment Steps

### 1. Create a New Project on Railway

1. Log in to your Railway dashboard
2. Click **"+ New Project"** → **"Empty Project"**
3. Give your project a name (e.g., "optimal-staking-demo")

### 2. Create the Service

1. In your project, click **"+ New"** → **"Empty Service"**
2. Name it "optimal-staking-app" (or similar)
3. Go to the service **Settings** tab:
   - Under **Source**, connect your GitHub repository
   - Set **Root Directory** to `/optimal-staking-demo`
   - Under **Build**, Railway should auto-detect the Dockerfile
4. Go to the **Settings** tab → **Networking**:
   - Click **"Generate Domain"** to create a public URL
   - Note this URL for accessing your application

**Important Note**: The `dockerfilePath` in `railway.json` must be relative to the repository root, not the service root directory. Since we set the root directory to `/optimal-staking-demo`, the Dockerfile path is configured as `optimal-staking-demo/Dockerfile`.

### 3. Configure Watch Paths (Optional)

To prevent unnecessary rebuilds when unrelated files change:

1. Go to **Settings** → **Watch Paths**
2. Add: `/optimal-staking-demo/**`

### 4. Deploy

Railway will automatically deploy the service when you:
- Push changes to your connected repository
- Make changes in the Railway dashboard
- Use the Railway CLI

## How It Works

The single-service deployment uses a multi-stage Docker build:

1. **Stage 1**: Builds the React frontend
   - Installs Node dependencies
   - Builds the production bundle
   
2. **Stage 2**: Sets up the Python backend
   - Installs Python dependencies
   - Copies the built frontend to the `static` directory
   - Configures FastAPI to serve both API and static files

## API Routes

- **Frontend**: Served at `/` (and all non-API routes for React routing)
- **API Endpoints**: All under `/api/*`
  - `/api/calculate` - Calculate tracking error
  - `/api/health` - Health check
  - `/api/docs/{filename}` - Documentation files

## Monitoring and Logs

1. Click on the service to view:
   - **Logs**: Real-time application logs
   - **Metrics**: CPU, memory, and network usage
   - **Deployments**: History of all deployments

2. Health check is configured at: `https://your-domain.railway.app/api/health`

## Local Development

For local development, the frontend and backend can still run separately:

```bash
# Backend (port 8000)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (port 5173, proxies API calls to backend)
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs in Railway dashboard
   - Ensure all dependencies are in `requirements.txt` and `package.json`
   - Verify the Dockerfile path is correct

2. **API Connection Issues**
   - Frontend automatically uses `/api` for all API calls
   - No CORS configuration needed in production
   - Check browser network logs for details

3. **Static Files Not Served**
   - Ensure the React build completes successfully
   - Check that static files are copied to the backend's `static` directory
   - Verify the multi-stage Docker build logs

### Useful Commands (Railway CLI)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to existing project
railway link

# Deploy from local directory
railway up

# View logs
railway logs

# Open project in browser
railway open
```

## Performance Benefits

This single-service architecture provides:
- **Reduced Latency**: API calls no longer cross network boundaries
- **Simplified Configuration**: No CORS or separate service URLs needed
- **Better Resource Utilization**: Single container uses resources more efficiently
- **Easier Debugging**: All logs in one place

## Production Considerations

1. **Security**
   - All secrets should be stored as Railway environment variables
   - Never commit `.env` files to version control
   - HTTPS is provided automatically by Railway

2. **Performance**
   - Static assets are served directly by FastAPI with proper caching
   - Docker image is optimized with multi-stage build
   - Health checks ensure service responsiveness

3. **Scaling**
   - Railway supports horizontal scaling through the dashboard
   - Monitor metrics to determine when scaling is needed
   - Single service architecture scales more predictably

## Cost Optimization

- Railway offers $5 free credits monthly
- Single service uses fewer resources than two separate services
- Monitor usage in the Railway dashboard
- Use sleep schedules for development environments

## Migration from Two-Service Setup

If migrating from the previous two-service setup:

1. Delete the old frontend and backend services
2. Create the new single service as described above
3. No environment variables needed for API URLs
4. Update any external references to use the single domain

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Project Issues: Create an issue in your GitHub repository