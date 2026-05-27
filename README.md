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
