# Prediction Investor

A multi-layer application for intelligent prediction market trading, combining a React frontend, FastAPI backend, and Spring Boot authentication service. Find at [herdmentality.curtischang.dev](herdmentality.curtischang.dev)

## Important!!
Change `frontend/Dockerfile`: \
`RUN npm ci --only=production` to `RUN npm ci` \
Change `python/.env`: \
`ENVIRONMENT=development` to `ENVIRONMENT=production` \
Add `keys/kalshi_rsa_key.key`
Change `springboot_auth/.env`: \
`BASE_URL=http://localhost:5173` to `BASE_URL=https://herdmentality.curtischang.dev`
`CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3001,http://127.0.0.1:5173,http://127.0.0.1:3001` to `CORS_ALLOWED_ORIGINS=https://herdmentality.curtischang.dev,http://localhost:5173,http://127.0.0.1:5173`

## Architecture

This application consists of three main layers orchestrated with Docker Compose:

### **Frontend** (`/frontend`)
- **Stack**: React + TypeScript + Vite
- **Purpose**: User interface for viewing polls, markets, and analytics
- **Port**: 5173 (mapped to 3000 in container)
- **Features**: Google OAuth integration, responsive UI

### **FastAPI Backend** (`/python`)
- **Stack**: Python FastAPI + MySQL + Redis
- **Purpose**: Core business logic, prediction market APIs (Kalshi), poll processing
- **Port**: 8000
- **Features**: Market data collection, automated poll processing, caching

### **Spring Boot Auth** (`/springboot_auth`)
- **Stack**: Spring Boot 3.5.6 + Java 21 + MySQL + Redis
- **Purpose**: User authentication, session management, email verification
- **Port**: 8080
- **Features**: Session-based auth, Google OAuth, password reset, email verification

### **Infrastructure**
- **MySQL 8.0**: Shared database for user data and application state
- **Redis 7**: Session storage and caching layer

---

## Deployment Setup

### Prerequisites
- Docker & Docker Compose installed on server
- SSH access to server
- Domain configured (optional, for production)

### Initial Server Setup

1. **Clone repository**
   ```bash
   git clone <your-repo-url> prediction_investor
   cd prediction_investor
   ```

2. **Create environment files** (see sections below)

3. **Create keys directory and add RSA key**
   ```bash
   mkdir -p python/keys
   # Upload kalshi_rsa_key.key to python/keys/
   chmod 600 python/keys/kalshi_rsa_key.key
   ```

4. **Deploy**
   ```bash
   docker-compose up -d
   ```

### Subsequent Deployments

```bash
cd prediction_investor
git pull origin main
docker-compose up -d --build
```

---

## Environment Variables Reference

All `.env` files are **not tracked in git** and must be created manually on the server.

### Root `.env`
Used by docker-compose for shared secrets.

```env
DATASOURCE_PASSWORD=your_mysql_root_password
```

### `frontend/.env`
Frontend API endpoints configuration.

```env
# Backend service URLs (use container names for Docker, localhost for local dev)
VITE_PYTHON_URL=http://fastapi:8000
VITE_SPRINGBOOT_URL=http://auth:8080
```

**Local Development:**
```env
VITE_PYTHON_URL=http://localhost:8000
VITE_SPRINGBOOT_URL=http://localhost:8080
```

### `python/.env`
FastAPI service configuration.

```env
# FastAPI Configuration
API_V1_STR=/api/v1
PROJECT_NAME="Herd Mentality"
INTERNAL_API_KEY=your_internal_api_key_here
PROCESS_EXPIRED_POLLS_MIN_INTERVAL=5
CREATE_POLL_HOUR_INTERVAL=36
ENVIRONMENT=production

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_KEY_PREFIX=python:

# Cache TTL settings (in seconds)
CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=3600
CACHE_TTL_LONG=86400

# MySQL Configuration
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_root_password
MYSQL_DATABASE=pidb

# Kalshi API Configuration
KALSHI_API_KEY=your_kalshi_api_key
KALSHI_RSA_KEY_PATH=/app/keys/kalshi_rsa_key.key
KALSHI_BASE_URL=https://trading-api.kalshi.com/trade-api/v2

# Spring Boot URL
SPRINGBOOT_URL=http://auth:8080
```

**Local Development:**
- Change `REDIS_HOST=localhost`
- Change `MYSQL_HOST=localhost`
- Change `SPRINGBOOT_URL=http://localhost:8080`
- Change `KALSHI_RSA_KEY_PATH` to absolute path on your system
- Change `ENVIRONMENT=development`

### `springboot_auth/.env`
Spring Boot authentication service configuration.

```env
# Server Configuration
BASE_URL=http://your-domain.com
CORS_ALLOWED_ORIGINS=http://your-domain.com,http://localhost:5173
REQUIRE_EMAIL_VERIFICATION=false
INTERNAL_API_KEY=your_internal_api_key_here

# OpenApi Configuration
APP_NAME="Herd Mentality"
SUPPORT_EMAIL=your_support_email@domain.com

# Redis
SPRING_REDIS_HOST=redis
SPRING_REDIS_PORT=6379

# Database Configuration
SPRING_DATASOURCE_HOSTNAME=mysql
SPRING_DATASOURCE_PORT=3306
SPRING_DATASOURCE_DB_NAME=pidb
SPRING_DATASOURCE_USERNAME=root
SPRING_DATASOURCE_PASSWORD=your_mysql_root_password

# Email Configuration (Gmail example)
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_FROM=noreply@yourdomain.com

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

**Local Development:**
- Change `SPRING_REDIS_HOST=localhost`
- Change `SPRING_DATASOURCE_HOSTNAME=localhost`
- Update `BASE_URL` and `CORS_ALLOWED_ORIGINS` to localhost URLs

---

## Required Files & Keys

### `python/keys/kalshi_rsa_key.key`
RSA private key for Kalshi API authentication. Must be created manually.

**Format:**
```
-----BEGIN RSA PRIVATE KEY-----
[Your RSA private key content here]
-----END RSA PRIVATE KEY-----
```

**Permissions:** `chmod 600 python/keys/kalshi_rsa_key.key`

---

## Quick Reference

### Start all services
```bash
docker-compose up -d
```

### Stop all services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f [service-name]
# Examples:
docker-compose logs -f frontend
docker-compose logs -f fastapi
docker-compose logs -f auth
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Check service health
```bash
docker-compose ps
```

---

## Port Mapping

| Service | Container Port | Host Port | Access |
|---------|---------------|-----------|--------|
| Frontend | 3000 | 5173 | http://localhost:5173 |
| FastAPI | 8000 | - | Internal only (via frontend) |
| Spring Boot | 8080 | - | Internal only (via frontend) |
| MySQL | 3306 | - | Internal only |
| Redis | 6379 | - | Internal only |

---

## Important Notes

- **Shared MySQL password**: Root `.env`, `python/.env`, and `springboot_auth/.env` must have matching `MYSQL_PASSWORD` values
- **Internal API Key**: `python/.env` and `springboot_auth/.env` should use the same `INTERNAL_API_KEY` for inter-service communication
- **Environment-specific hosts**: Use container names (`redis`, `mysql`, `auth`, `fastapi`) in Docker, `localhost` for local development
- **Email setup**: Gmail requires "App Passwords" - see [Google Account Help](https://support.google.com/accounts/answer/185833)
- **Google OAuth**: Obtain credentials from [Google Cloud Console](https://console.cloud.google.com/)

---

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Verify .env files exist
ls -la .env frontend/.env python/.env springboot_auth/.env

# Verify keys directory
ls -la python/keys/
```

### Database connection issues
```bash
# Check MySQL is healthy
docker-compose ps mysql

# Verify password consistency across .env files
grep MYSQL_PASSWORD .env python/.env springboot_auth/.env
```

### Redis connection issues
```bash
# Check Redis is healthy
docker-compose exec redis redis-cli ping
```

---

## Development vs Production

**Development:**
- Use `localhost` for all service hosts in `.env` files
- Expose ports in `docker-compose.yml` (uncomment `ports:` sections)
- Set `ENVIRONMENT=development` in `python/.env`

**Production:**
- Use container names (`redis`, `mysql`, etc.) in `.env` files
- Keep ports internal (comment out `ports:` sections)
- Set `ENVIRONMENT=production` in `python/.env`
- Enable `REQUIRE_EMAIL_VERIFICATION=true`
- Use HTTPS and proper domain names
