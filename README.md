# Gateway-Hub
A minimal, production-ready URL-shortening service with free & premium tiers. Built with FastAPI + PostgreSQL (dev-friendly defaults included).

🚀 Gateway Hub — Minimal URL‑Shortening SaaS (Free & Premium Tiers)
Gateway Hub is a lightweight, production‑ready SaaS application that provides URL shortening with free and premium subscription tiers.
It is built with FastAPI + SQLAlchemy + PostgreSQL, and can run on low-cost VPS infrastructure or container platforms.

This project is intentionally minimal, easy to deploy, and designed to be extended into a full SaaS product.

✨ Features
Free Tier
Create up to 5 short links per month

Up to 100 clicks per link

Personal dashboard for managing links

Premium Tier
Unlimited short links

Unlimited clicks

Click analytics (basic)

Custom domain support (demo placeholder)

Priority usage limits

Note: Payment flow is mocked for demonstration. The mock upgrade endpoint is disabled when `ENVIRONMENT=production` unless `ENABLE_MOCK_BILLING=true` is explicitly set for a controlled demo. In production, integrate Stripe, PayPal, or another billing provider.

🏗️ Tech Stack
Python 3.10+

FastAPI (web framework)

PostgreSQL (primary database)

Werkzeug (password hashing)

REST API + React frontend

📁 Project Structure
Код
Gateway-Hub/
│
├── app/                 # FastAPI backend
├── src/                 # React/TypeScript frontend
├── migrations/          # Alembic migrations
├── requirements.txt     # Python dependencies
├── package.json         # Frontend dependencies
└── README.md            # Project documentation
📦 Installation
Clone the repository:

bash
git clone https://github.com/AlexKitipov/Gateway-Hub
cd Gateway-Hub
Install dependencies:

bash
pip install -r requirements.txt
🗄️ Database Setup
Run migrations (configure your database URL first in environment variables):

bash
alembic upgrade head

This creates the required PostgreSQL schema. The application does not create or update tables at runtime; run Alembic migrations before starting or restarting the API in every deployment.

▶️ Running the Application
bash
uvicorn app.main:app --reload
The service will be available at:

Код
http://127.0.0.1:8000
🔐 Security Notes
Replace the default dev-secret-key with a secure key in production. The application refuses to start when `ENVIRONMENT=production` and `SECRET_KEY` is blank or still set to a placeholder value.

Keep `ENABLE_MOCK_BILLING=false` in production so demo premium upgrades cannot grant paid access. The Stripe placeholder settings (`STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`, `STRIPE_SUCCESS_URL`, and `STRIPE_CANCEL_URL`) are reserved for the production billing integration.

Configure short-link generation with `SHORT_CODE_LENGTH`, `SHORT_CODE_ALPHABET`, and `SHORT_URL_BASE` (for example, `https://yourdomain.com/r`). `ALLOWED_ORIGINS` accepts a comma-separated list such as `https://app.example.com,https://admin.example.com`.

Always run behind HTTPS.

Consider adding:

CSRF protection for browser-only flows

Structured logging & monitoring enhancements

Reverse proxy (Nginx) + Gunicorn for production

📈 Future Enhancements
Real payment integration (Stripe / PayPal)

Custom domain routing

QR code generation

REST API for programmatic shortening

Admin dashboard

Email notifications

Analytics dashboard with charts

📝 License
This project is licensed under the MIT License.
You are free to use, modify, and deploy it commercially.


## 5. REST API Specification

All authenticated and management API endpoints are versioned under `/api/v1`. Public short-link redirects are served separately at `/r/{code}` so they stay short and do not collide with the links API.

### 5.1 Authentication Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| POST | `/api/v1/auth/register` | ❌ | 5/min | Register new user |
| POST | `/api/v1/auth/login` | ❌ | 10/min | User login |
| POST | `/api/v1/auth/logout` | ✅ | 100/min | User logout |
| POST | `/api/v1/auth/refresh` | ❌ | 10/min | Refresh access token |

**Register**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

Response `201`:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_premium": false,
    "is_active": true,
    "premium_until": null,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Login**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

Response `200`:

```json
{
  "user": { "...": "..." },
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 5.2 User Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| GET | `/api/v1/users/stats` | ✅ | 100/min | Get user stats |
| POST | `/api/v1/users/upgrade` | ✅ | 1/min | Upgrade to premium |

**Get Stats**

```http
GET /api/v1/users/stats
Authorization: Bearer <token>
```

Response `200`:

```json
{
  "total_links": 12,
  "total_clicks": 1523,
  "links_this_month": 3,
  "is_premium": false,
  "premium_until": null
}
```

**Upgrade**

```http
POST /api/v1/users/upgrade
Authorization: Bearer <token>
```

Response `200` (development/demo mock billing only):

```json
{
  "success": true,
  "message": "Upgraded to premium",
  "premium_until": "2025-01-15T10:30:00Z"
}
```

Response `403` when `ENVIRONMENT=production` and `ENABLE_MOCK_BILLING=false`:

```json
{
  "detail": "Mock premium upgrades are disabled in production. Configure Stripe billing or set ENABLE_MOCK_BILLING=true only for controlled demos."
}
```

### 5.3 Links Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| GET | `/api/v1/links/` | ✅ | 100/min | Get user's links |
| POST | `/api/v1/links/create` | ✅ | 30/min | Create new link |
| DELETE | `/api/v1/links/{code}` | ✅ | 100/min | Delete link |
| GET | `/api/v1/links/{code}` | ✅ | 100/min | Get link details |

**Create Link**

```http
POST /api/v1/links/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "target_url": "https://example.com/very-long-url",
  "title": "Example Link",
  "description": "My test link",
  "custom_code": null
}
```

Response `201`:

```json
{
  "id": 42,
  "code": "abc123",
  "target_url": "https://example.com/very-long-url",
  "title": "Example Link",
  "description": "My test link",
  "click_count": 0,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "short_url": "https://sh.rt/abc123"
}
```

**Get All Links**

```http
GET /api/v1/links/?skip=0&limit=50
Authorization: Bearer <token>
```

Response `200`:

```json
{
  "total": 12,
  "limit": 50,
  "offset": 0,
  "links": [
    {
      "id": 42,
      "code": "abc123",
      "target_url": "https://example.com/...",
      "title": "Example Link",
      "click_count": 15,
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "short_url": "https://sh.rt/abc123"
    }
  ]
}
```

**Delete Link**

```http
DELETE /api/v1/links/abc123
Authorization: Bearer <token>
```

Response `200`:

```json
{
  "success": true,
  "message": "Link deleted successfully"
}
```

**Public Redirect**

```http
GET /r/abc123
```

Response: `301 Moved Permanently`

```http
Location: https://example.com/very-long-url
```

### 5.4 Public Redirect Endpoint

Public redirects are intentionally outside the `/api/v1` management API and are handled by the dedicated redirect router.

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| GET | `/r/{code}` | ❌ | 1000/min | Redirect to the target URL and record click analytics |

### 5.5 Analytics Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| GET | `/api/v1/analytics/{code}` | ✅ | 100/min | Get link analytics |

**Get Analytics**

```http
GET /api/v1/analytics/abc123?days=30
Authorization: Bearer <token>
```

Response `200`:

```json
{
  "link_code": "abc123",
  "total_clicks": 1523,
  "unique_ips": 256,
  "top_countries": [["US", 450], ["GB", 300], ["CA", 200]],
  "top_referrers": [["https://twitter.com", 500], ["https://reddit.com", 400], ["Direct", 623]],
  "clicks_by_date": [["2024-01-15", 50], ["2024-01-16", 75], ["2024-01-17", 120]],
  "clicks_by_hour": [[0, 5], [1, 3], [8, 45], [12, 120], [23, 8]]
}
```

### 5.6 Error Response Format

All errors use:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE_CONSTANT"
}
```

| Code | Status | Meaning |
|---|---|---|
| `INVALID_CREDENTIALS` | 401 | Wrong email/password |
| `INVALID_TOKEN` | 401 | JWT token expired or invalid |
| `UNAUTHORIZED` | 403 | No authentication provided |
| `USER_NOT_FOUND` | 404 | User does not exist |
| `LINK_NOT_FOUND` | 404 | Short link does not exist |
| `EMAIL_ALREADY_EXISTS` | 400 | Email already registered |
| `LIMIT_EXCEEDED` | 403 | Free tier limit reached |
| `CLICK_LIMIT_EXCEEDED` | 403 | Free tier click limit exceeded |
| `CODE_TAKEN` | 400 | Custom code already in use |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

## 8. PRODUCTION DEPLOYMENT STRATEGY

### 8.1 VPS Setup (DigitalOcean / Linode / Hetzner)

**Recommended Specs:**

- OS: Ubuntu 22.04 LTS
- CPU: 1 vCore
- RAM: 2GB
- Storage: 50GB SSD
- Cost: $6-12/month

**Initial Setup (non-interactive):**

The repository includes `deploy.sh`, which is designed to be rerunnable and suitable for automation. It installs packages, creates the application user if needed, clones or fast-forwards the repository, creates or preserves the production environment file, runs Alembic migrations after that environment is available, installs systemd/Nginx, and restarts services.

```bash
# Run on the VPS as root, or via sudo from an administrator account.
sudo APP_USER=appuser \
  APP_DIR=/home/appuser/backend \
  REPO_URL=https://github.com/AlexKitipov/Gateway-Hub.git \
  REPO_BRANCH=main \
  ./deploy.sh
```

Optional settings:

- `RUN_APT_UPGRADE=true` also applies package upgrades; by default the script only updates package metadata and installs missing dependencies.
- `ENABLE_SSL=true DOMAIN=api.example.com CERTBOT_EMAIL=admin@example.com` requests a Let's Encrypt certificate without prompts.
- `ENV_FILE=/etc/gateway-hub/gateway-hub.env` overrides the systemd environment file location.

The first run creates `/etc/gateway-hub/gateway-hub.env` with mode `0640`, owner `root`, and group `appuser`. It generates a unique `SECRET_KEY` instead of committing or hardcoding one. Review the file before exposing the service, especially `ALLOWED_ORIGINS` and any provider credentials.

Example environment file:

```dotenv
DATABASE_URL=postgresql:///gateway_hub
SECRET_KEY=<generated-or-secret-manager-value>
DEBUG=false
ENVIRONMENT=production
ALLOWED_ORIGINS=https://app.example.com
REDIS_URL=redis://localhost:6379
```

Migrations must run with the same environment as the service. `deploy.sh` sources `/etc/gateway-hub/gateway-hub.env` before running `./scripts/migrate.sh`, so schema changes are applied to the configured production database before the API is restarted.

### 8.2 Systemd Service File

```ini
# /etc/systemd/system/gateway-hub.service
[Unit]
Description=Gateway Hub API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=appuser
WorkingDirectory=/home/appuser/backend
Environment="PATH=/home/appuser/backend/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/etc/gateway-hub/gateway-hub.env
ExecStart=/home/appuser/backend/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --timeout-keep-alive 65 \
    --access-log

Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

`Type=simple` matches the direct `uvicorn` process above. Use `Type=notify` only if you add a notify-capable wrapper that sends systemd readiness notifications.

**Commands:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable gateway-hub
sudo systemctl start gateway-hub
sudo systemctl status gateway-hub
sudo journalctl -u gateway-hub -f  # View logs
```

### 8.3 Nginx Reverse Proxy Configuration

```nginx
# /etc/nginx/sites-available/gateway-hub
upstream gateway_hub_backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=5 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # Logging
    access_log /var/log/nginx/gateway-hub-access.log;
    error_log /var/log/nginx/gateway-hub-error.log;

    # API endpoints
    location /api/ {
        proxy_pass http://gateway_hub_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Public redirect endpoint (short URLs)
    location ~ ^/r/[a-zA-Z0-9_-]+$ {
        proxy_pass http://gateway_hub_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend (separate domain)
    location / {
        return 404;  # API-only, frontend on separate domain
    }
}
```

**Setup SSL with Let's Encrypt:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.yourdomain.com
```

### 8.4 Docker Compose Full-Stack Setup

Docker Compose can run the complete local stack: FastAPI backend, React frontend, PostgreSQL, Redis, and an optional Nginx reverse proxy.

**Services included:**

- `postgres` — PostgreSQL 15 database used by the backend.
- `redis` — Redis 7 cache/rate-limit store used by the backend.
- `migrate` — one-shot Alembic migration job that runs before the backend starts.
- `backend` — FastAPI API served by Uvicorn on `http://localhost:8000` by default.
- `frontend` — production React static build served by Nginx on `http://localhost:3000` by default.
- `nginx` — optional reverse proxy profile on `http://localhost:8080` that routes `/api/` and `/r/` to the backend and all other requests to the frontend.

**Prepare environment variables:**

```bash
cp .env.example .env
```

The backend uses synchronous SQLAlchemy/psycopg2, so Compose uses a sync PostgreSQL URL:

```env
DATABASE_URL=postgresql://appuser:password123@postgres:5432/gateway_hub
REDIS_URL=redis://redis:6379
REACT_APP_API_URL=http://localhost:8000
```

**Start the default local stack:**

```bash
docker compose up --build
```

The `migrate` job runs `alembic upgrade head` automatically after PostgreSQL is healthy. The backend waits for that job to complete successfully before it starts, so a normal `docker compose up` creates a coherent application stack without a separate migration command.

**Open the application:**

- Frontend: `http://localhost:3000`
- Backend health check: `http://localhost:8000/health`
- API base path: `http://localhost:8000/api/v1`

**Run with the optional Nginx reverse proxy:**

```bash
docker compose --profile proxy up --build
```

When the `proxy` profile is enabled, open `http://localhost:8080`. Nginx serves the frontend and proxies API calls to the backend from the same origin.

**Database and Redis ports:**

PostgreSQL and Redis are intentionally not published to the host by default. They are reachable by other Compose services on the internal Docker network as `postgres:5432` and `redis:6379`, which avoids exposing database/cache ports in production-like runs. If you need host access for a local database client, add a temporary `docker-compose.override.yml` such as:

```yaml
services:
  postgres:
    ports:
      - "5432:5432"
  redis:
    ports:
      - "6379:6379"
```

**Useful commands:**

```bash
# Re-run migrations manually if needed
docker compose run --rm migrate

# Follow backend logs
docker compose logs -f backend

# Stop and remove containers, keeping named volumes
docker compose down

# Stop and remove containers plus database/cache volumes
docker compose down -v
```

### 8.5 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
        run: pytest tests/ --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: appuser
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/backend
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            alembic upgrade head
            systemctl restart gateway-hub
            systemctl status gateway-hub
```

### 8.6 Monitoring & Logging

```python
# Structured logging setup
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.FileHandler('logs/app.json')
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log important events
logger.info("User registered", extra={
    "user_id": user.id,
    "email": user.email,
    "timestamp": datetime.utcnow().isoformat()
})

logger.error("Link creation failed", extra={
    "user_id": user_id,
    "reason": str(e),
    "timestamp": datetime.utcnow().isoformat()
})
```

**Monitoring Tools (Optional):**

- Uptime Monitoring: Uptimerobot.com (free)
- Application Monitoring: Sentry.io (free tier available)
- Log Aggregation: Papertrail, Datadog, ELK Stack
- Performance: New Relic, Datadog APM
