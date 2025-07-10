# Railway.app Universal Deployment Guide

A comprehensive guide for deploying any project type on Railway.app, from simple APIs to complex full-stack applications.

## Table of Contents
1. [Railway Fundamentals](#railway-fundamentals)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Configuration Files](#configuration-files)
4. [Dockerfile Templates](#dockerfile-templates)
5. [Environment Variables](#environment-variables)
6. [Deployment Methods](#deployment-methods)
7. [Common Project Types](#common-project-types)
8. [Advanced Configurations](#advanced-configurations)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Railway Fundamentals

### What Railway Provides
- **Automatic HTTPS**: SSL certificates managed automatically
- **Environment Variables**: `PORT`, `RAILWAY_PUBLIC_DOMAIN`, `RAILWAY_ENVIRONMENT`
- **Git Integration**: Auto-deploy on push
- **Database Support**: PostgreSQL, MySQL, MongoDB, Redis
- **Persistent Storage**: Volume mounts available
- **Custom Domains**: Easy domain configuration
- **Private Networking**: Internal service communication

### Build Detection Order
1. `railway.json` configuration
2. `Dockerfile` presence
3. Nixpacks auto-detection (if no Dockerfile)

## Pre-Deployment Checklist

### Essential Files
- [ ] `Dockerfile` or buildpack-compatible structure
- [ ] `.dockerignore` to exclude unnecessary files
- [ ] `railway.json` (optional but recommended)
- [ ] Environment variable list
- [ ] Start command defined

### Project Requirements
- [ ] All dependencies declared (package.json, requirements.txt, etc.)
- [ ] Database migrations handled
- [ ] Static assets properly served
- [ ] Health check endpoint (recommended)
- [ ] Graceful shutdown handling

## Configuration Files

### railway.json Structure
```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile",
    "buildCommand": "echo 'Custom build step'"
  },
  "deploy": {
    "startCommand": "npm start",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "region": "us-west1"
  }
}
```

### .dockerignore Template
```
# Version control
.git
.gitignore

# Dependencies
node_modules
venv
env
__pycache__
*.pyc

# Development
.env
.env.local
*.log
.DS_Store
.vscode
.idea

# Testing
coverage
.pytest_cache
*.test.js
*.spec.ts

# Documentation
README.md
docs/
*.md

# Build artifacts
dist
build
.next
.nuxt
```

## Dockerfile Templates

### Python Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Use Railway's PORT variable
CMD ["python", "-m", "gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
```

### Node.js Backend
```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

# Use Railway's PORT variable
CMD ["node", "server.js"]
```

### Full-Stack (React + Express)
```dockerfile
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Build React app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Final stage
FROM node:20-alpine

WORKDIR /app

# Copy backend
COPY backend/package*.json ./
RUN npm ci --only=production
COPY backend/ .

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./public

# Non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

EXPOSE 8080
CMD ["node", "server.js"]
```

### Python + Node.js (MCP Servers)
```dockerfile
FROM nikolaik/python-nodejs:python3.11-nodejs20-slim

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node global tools
RUN npm install -g npx

# Copy application
COPY . .

# Install project (if using setup.py)
RUN pip install -e .

CMD ["python", "app.py"]
```

### Next.js Application
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

CMD ["node", "server.js"]
```

## Environment Variables

### Railway Provided Variables
```bash
PORT                    # Port your app should listen on
RAILWAY_PUBLIC_DOMAIN   # Your app's public URL
RAILWAY_ENVIRONMENT     # Environment name (production, staging)
RAILWAY_GIT_COMMIT_SHA  # Current deployment commit
RAILWAY_GIT_BRANCH      # Deployed branch name
```

### Setting Variables in Railway

#### Via Dashboard
1. Navigate to project → Variables tab
2. Add key-value pairs
3. Click "Add" for each variable
4. **IMPORTANT**: Click "Deploy" to apply changes

#### Via CLI
```bash
railway variables set KEY=value
railway variables set -e production KEY=value
```

#### Via railway.json
```json
{
  "environments": {
    "production": {
      "NODE_ENV": "production",
      "LOG_LEVEL": "info"
    }
  }
}
```

### Environment-Specific Files
Create `.env.example`:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# API Keys
API_KEY=your-api-key
SECRET_KEY=your-secret-key

# App Config
NODE_ENV=production
LOG_LEVEL=info
```

## Deployment Methods

### Method 1: GitHub Integration
```bash
# In Railway Dashboard:
1. New Project → Deploy from GitHub repo
2. Select repository
3. Configure environment variables
4. Railway auto-deploys on push
```

### Method 2: Railway CLI
```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Link existing project
railway link [projectId]

# Deploy
railway up

# Deploy specific environment
railway up -e production
```

### Method 3: Docker Image
```bash
# Build and push to registry
docker build -t myapp:latest .
docker tag myapp:latest registry.railway.app/project/service:latest
docker push registry.railway.app/project/service:latest

# Configure in railway.json
{
  "build": {
    "builder": "DOCKER",
    "image": "registry.railway.app/project/service:latest"
  }
}
```

## Common Project Types

### FastAPI Application
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

**railway.json:**
```json
{
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ALWAYS"
  }
}
```

### Django Application
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "myproject.wsgi", "--bind", "0.0.0.0:$PORT"]
```

**Start script (start.sh):**
```bash
#!/bin/bash
python manage.py migrate
gunicorn myproject.wsgi --bind 0.0.0.0:$PORT
```

### Monorepo Structure
```dockerfile
# For apps/api
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
COPY apps/api/package*.json ./apps/api/
RUN npm ci
COPY . .
WORKDIR /app/apps/api
CMD ["npm", "start"]
```

**railway.json:**
```json
{
  "build": {
    "dockerfilePath": "./apps/api/Dockerfile"
  }
}
```

### Static Site + API
```nginx
# nginx.conf
server {
    listen $PORT;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

## Advanced Configurations

### Multi-Stage Health Checks
```javascript
// healthcheck.js
const checks = {
  database: async () => {
    return await db.query('SELECT 1');
  },
  redis: async () => {
    return await redis.ping();
  },
  external: async () => {
    return await fetch('https://api.example.com/health');
  }
};

app.get('/health', async (req, res) => {
  const results = await Promise.allSettled(
    Object.entries(checks).map(async ([name, check]) => ({
      name,
      status: await check().then(() => 'ok').catch(() => 'error')
    }))
  );
  
  const allOk = results.every(r => r.value.status === 'ok');
  res.status(allOk ? 200 : 503).json({ checks: results });
});
```

### Graceful Shutdown
```javascript
// Node.js example
const server = app.listen(process.env.PORT);

process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

### Database Migrations
```dockerfile
# Migration stage
FROM migrate/migrate AS migrator
COPY ./migrations /migrations
CMD ["migrate", "-path", "/migrations", "-database", "$DATABASE_URL", "up"]

# App stage
FROM node:20-alpine
# ... rest of Dockerfile
```

### Startup Scripts
```python
#!/usr/bin/env python3
# startup.py
import os
import sys
import subprocess

def setup_environment():
    """Configure runtime environment"""
    # Convert env vars to files if needed
    if secret_json := os.getenv('SECRET_JSON'):
        with open('/tmp/secret.json', 'w') as f:
            f.write(secret_json)
        os.environ['SECRET_FILE'] = '/tmp/secret.json'

def run_migrations():
    """Run database migrations"""
    subprocess.run(['python', 'manage.py', 'migrate'], check=True)

def main():
    setup_environment()
    run_migrations()
    # Start main app
    subprocess.run(['python', 'app.py'])

if __name__ == '__main__':
    main()
```

## Troubleshooting

### Common Issues and Solutions

#### Port Binding Errors
```bash
# Wrong
app.listen(3000)  # Hardcoded port

# Correct
app.listen(process.env.PORT || 3000)
```

#### Environment Variables Not Available
1. Check Variables tab in Railway dashboard
2. Ensure you clicked "Deploy" after adding variables
3. Verify with: `railway run env | grep YOUR_VAR`

#### Build Failures
```dockerfile
# Add build debugging
RUN echo "Current directory:" && pwd
RUN echo "Files:" && ls -la
RUN echo "Node version:" && node --version
```

#### Memory Issues
```json
{
  "deploy": {
    "maxMemory": "2048"
  }
}
```

#### Timezone Issues
```dockerfile
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
```

### Debugging Commands
```bash
# View logs
railway logs

# Connect to service
railway run bash

# Check environment
railway run env

# Test locally with Railway env
railway run npm start
```

## Best Practices

### 1. Security
- Never hardcode secrets
- Use non-root users in containers
- Keep base images updated
- Scan for vulnerabilities

### 2. Performance
- Multi-stage builds for smaller images
- Cache dependencies layers
- Use `.dockerignore` effectively
- Enable gzip compression

### 3. Reliability
- Implement health checks
- Handle graceful shutdown
- Use restart policies
- Log to stdout/stderr

### 4. Development Workflow
```yaml
# .github/workflows/railway-preview.yml
name: Railway Preview
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railwayapp/deploy-action@v1
        with:
          service: my-app
          environment: preview-${{ github.event.pull_request.number }}
```

### 5. Monitoring
- Use structured logging
- Set up alerts for failures
- Monitor resource usage
- Track deployment metrics

### 6. Cost Optimization
- Use appropriate instance sizes
- Clean up unused services
- Optimize build caching
- Monitor usage patterns

## Quick Reference

### Essential Commands
```bash
railway login              # Authenticate
railway init              # Create project
railway up                # Deploy
railway logs              # View logs
railway run [cmd]         # Run with env vars
railway variables set     # Set env var
railway open              # Open dashboard
railway restart           # Restart service
```

### Useful Patterns
```bash
# Local development with Railway env
railway run npm run dev

# Run one-off tasks
railway run python manage.py createsuperuser

# Debug environment
railway run printenv | sort

# Connect to database
railway run psql $DATABASE_URL
```

This guide should enable any coding agent to successfully deploy projects on Railway.app across various technology stacks and configurations.