# Railway Deployment Guide for Staking TD Demo

This guide provides step-by-step instructions for deploying the Staking Tracking Error Demo application to Railway.app.

## Prerequisites

- A Railway account (sign up at [railway.app](https://railway.app))
- Git repository with your code pushed to GitHub/GitLab/Bitbucket
- Railway CLI (optional, for local deployment)

## Project Structure

The application consists of two services:
- **Backend**: FastAPI Python application
- **Frontend**: React TypeScript application served by Caddy

## Deployment Steps

### 1. Create a New Project on Railway

1. Log in to your Railway dashboard
2. Click **"+ New Project"** → **"Empty Project"**
3. Give your project a name (e.g., "optimal-staking-demo")

### 2. Create Backend Service

1. In your project, click **"+ New"** → **"Empty Service"**
2. Name it "backend" (or similar)
3. Go to the service **Settings** tab:
   - Under **Source**, connect your GitHub repository
   - Set **Root Directory** to `/optimal-staking-demo/backend`
   - Under **Build**, Railway should auto-detect the Dockerfile
4. Go to the **Variables** tab and add:
   ```
   FRONTEND_URL=https://your-frontend-service.railway.app
   ```
   (You'll update this after creating the frontend service)
5. Go to the **Settings** tab → **Networking**:
   - Click **"Generate Domain"** to create a public URL
   - Note this URL for the frontend configuration

### 3. Create Frontend Service

1. In your project, click **"+ New"** → **"Empty Service"**
2. Name it "frontend" (or similar)
3. Go to the service **Settings** tab:
   - Under **Source**, connect your GitHub repository
   - Set **Root Directory** to `/optimal-staking-demo/frontend`
   - Under **Build**, Railway should auto-detect the Dockerfile
4. Go to the **Variables** tab and add:
   ```
   VITE_API_URL=https://your-backend-service.railway.app
   ```
   (Use the backend URL from step 2.5)
5. Go to the **Settings** tab → **Networking**:
   - Click **"Generate Domain"** to create a public URL

### 4. Update Backend CORS Settings

1. Go back to your backend service
2. Update the `FRONTEND_URL` variable with the frontend URL from step 3.5
3. The backend will automatically redeploy with the correct CORS settings

### 5. Configure Watch Paths (Optional but Recommended)

To prevent unnecessary rebuilds when only one service changes:

1. **Backend Service** → **Settings** → **Watch Paths**:
   - Add: `/optimal-staking-demo/backend/**`
2. **Frontend Service** → **Settings** → **Watch Paths**:
   - Add: `/optimal-staking-demo/frontend/**`

### 6. Deploy

Railway will automatically deploy both services when you:
- Push changes to your connected repository
- Make changes in the Railway dashboard
- Use the Railway CLI

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Automatically provided by Railway | `8000` |
| `FRONTEND_URL` | Frontend URL for CORS | `https://frontend.railway.app` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://backend.railway.app` |

## Monitoring and Logs

1. Click on any service to view:
   - **Logs**: Real-time application logs
   - **Metrics**: CPU, memory, and network usage
   - **Deployments**: History of all deployments

2. Health checks are configured at:
   - Backend: `https://your-backend.railway.app/health`
   - Frontend: Caddy handles health checks automatically

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure `FRONTEND_URL` in backend matches your frontend domain exactly
   - Check that the backend is using HTTPS in production

2. **Port Binding Errors**
   - Backend must bind to `0.0.0.0:$PORT` (not `localhost` or `127.0.0.1`)
   - Frontend Caddy server automatically uses `$PORT`

3. **Build Failures**
   - Check build logs in Railway dashboard
   - Ensure all dependencies are in `requirements.txt` (backend) or `package.json` (frontend)
   - Verify Dockerfile paths are correct

4. **API Connection Issues**
   - Verify `VITE_API_URL` in frontend points to backend's public URL
   - Ensure both services have generated public domains
   - Check network logs in browser developer tools

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

## Production Considerations

1. **Security**
   - All secrets should be stored as Railway environment variables
   - Never commit `.env` files to version control
   - Use HTTPS for all communications (Railway provides this automatically)

2. **Performance**
   - Docker images are optimized with multi-stage builds
   - Static assets are served with proper caching headers via Caddy
   - Health checks ensure services stay responsive

3. **Scaling**
   - Railway supports horizontal scaling through the dashboard
   - Monitor metrics to determine when scaling is needed
   - Consider implementing rate limiting for the API

## Cost Optimization

- Railway offers $5 free credits monthly
- Monitor usage in the Railway dashboard
- Use sleep schedules for development environments
- Optimize Docker images to reduce build times

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Project Issues: Create an issue in your GitHub repository