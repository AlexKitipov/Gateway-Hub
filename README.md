# Gateway-Hub
A minimal, production‑ready URL‑shortening service with free &amp; premium tiers. Built with Flask + SQLite, deployable on any cheap VPS or serverless platform.

🚀 Gateway Hub — Minimal URL‑Shortening SaaS (Free & Premium Tiers)
Gateway Hub is a lightweight, production‑ready SaaS application that provides URL shortening with free and premium subscription tiers.
It is built with Flask + SQLite, requires no external database, and can run on any low‑cost VPS or serverless platform.

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

Note: Payment flow is mocked for demonstration.
In production, integrate Stripe, PayPal, or another billing provider.

🏗️ Tech Stack
Python 3.10+

Flask (web framework)

SQLite (embedded database)

Werkzeug (password hashing)

HTML templates inline for simplicity

📁 Project Structure
Код
Gateway-Hub/
│
├── app.py               # Main Flask application
├── schema.sql           # Database schema
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── LICENSE              # MIT license
└── .gitignore
📦 Installation
Clone the repository:

bash
git clone https://github.com/AlexKitipov/Gateway-Hub
cd Gateway-Hub
Install dependencies:

bash
pip install -r requirements.txt
🗄️ Database Setup
Initialize the SQLite database:

bash
python
>>> from app import init_db
>>> init_db()
This creates shortener.db with all required tables.

▶️ Running the Application
bash
python app.py
The service will be available at:

Код
http://127.0.0.1:5000
🔐 Security Notes
Replace the default dev-secret-key with a secure key in production.

Always run behind HTTPS.

Consider adding:

CSRF protection (Flask‑WTF)

Rate limiting (Flask‑Limiter)

Logging & monitoring

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

All endpoints are versioned under `/api/v1`.

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
| GET | `/api/v1/user/stats` | ✅ | 100/min | Get user stats |
| POST | `/api/v1/user/upgrade` | ✅ | 1/min | Upgrade to premium |

**Get Stats**

```http
GET /api/v1/user/stats
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
POST /api/v1/user/upgrade
Authorization: Bearer <token>
```

Response `200`:

```json
{
  "success": true,
  "message": "Upgraded to premium",
  "premium_until": "2025-01-15T10:30:00Z"
}
```

### 5.3 Links Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|---|---|---|---|---|
| GET | `/api/v1/links/` | ✅ | 100/min | Get user's links |
| POST | `/api/v1/links/create` | ✅ | 30/min | Create new link |
| DELETE | `/api/v1/links/{code}` | ✅ | 100/min | Delete link |
| GET | `/api/v1/links/{code}` | ✅ | 100/min | Get link details |
| GET | `/api/v1/links/r/{code}` | ❌ | 1000/min | Redirect (public) |

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
GET /api/v1/links/r/abc123
```

Response: `301 Moved Permanently`

```http
Location: https://example.com/very-long-url
```

### 5.4 Analytics Endpoints

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

### 5.5 Error Response Format

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
