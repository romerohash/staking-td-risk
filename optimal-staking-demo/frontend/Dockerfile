# Build stage
FROM node:18-alpine AS builder

# Accept build arguments
ARG VITE_API_URL

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set environment variable for build
ENV VITE_API_URL=$VITE_API_URL

# Build the React app
RUN npm run build

# Production stage
FROM caddy:2-alpine

# Copy built React app from builder stage
COPY --from=builder /app/dist /srv

# Copy Caddy configuration
COPY Caddyfile /etc/caddy/Caddyfile

# Create necessary directories and set permissions
RUN mkdir -p /data /config /srv && \
    adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /srv /data /config /etc/caddy

# Set Caddy environment variables to use writable directories
ENV XDG_DATA_HOME=/data
ENV XDG_CONFIG_HOME=/config

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-80}/ || exit 1

# Railway will set the PORT environment variable
EXPOSE ${PORT:-80}