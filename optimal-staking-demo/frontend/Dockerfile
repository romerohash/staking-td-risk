# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Production stage
FROM caddy:2-alpine

# Copy built React app from builder stage
COPY --from=builder /app/dist /srv

# Copy Caddy configuration
COPY Caddyfile /etc/caddy/Caddyfile

# Create non-root user
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /srv
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-80}/ || exit 1

# Railway will set the PORT environment variable
EXPOSE ${PORT:-80}