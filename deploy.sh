#!/bin/bash
# deploy.sh - Complete deployment script

set -e

echo "🚀 Gateway Hub Deployment Script"

# 1. Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
echo "📥 Installing dependencies..."
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git redis-server certbot python3-certbot-nginx

# 3. Create app user
if ! id "appuser" &>/dev/null; then
    echo "👤 Creating appuser..."
    sudo useradd -m -s /bin/bash appuser
fi

# 4. Clone repository
echo "📂 Cloning repository..."
cd /home/appuser
sudo -u appuser git clone https://github.com/AlexKitipov/Gateway-Hub.git backend || true
cd backend

# 5. Setup Python environment
echo "🐍 Setting up Python virtual environment..."
sudo -u appuser python3 -m venv venv
sudo -u appuser venv/bin/pip install --upgrade pip
sudo -u appuser venv/bin/pip install -r requirements.txt

# 6. Setup database
echo "🗄️  Setting up PostgreSQL..."
sudo -u postgres createdb gateway_hub || true

# 7. Create .env file before migrations so Alembic uses production settings
echo "⚙️  Creating environment configuration..."
if [ ! -f .env ]; then
    sudo -u appuser cp .env.example .env
fi
echo "⚠️  Please edit /home/appuser/backend/.env with production values"
read -p "Press Enter after updating .env..."

# 8. Run migrations explicitly before starting the application
echo "🧬 Running database migrations..."
sudo -u appuser ./scripts/migrate.sh

# 9. Setup systemd service
echo "🔧 Setting up systemd service..."
sudo cp gateway-hub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gateway-hub

# 10. Setup Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx/gateway-hub.conf /etc/nginx/sites-available/gateway-hub
sudo ln -sf /etc/nginx/sites-available/gateway-hub /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 11. Setup SSL with Let's Encrypt
echo "🔒 Setting up SSL certificates..."
read -p "Enter your domain for SSL (e.g., api.example.com): " domain
sudo certbot certonly --nginx -d $domain

# 12. Start services
echo "▶️  Starting services..."
sudo systemctl start gateway-hub
sudo systemctl start redis-server

# 13. Verify
echo "✅ Checking service status..."
sudo systemctl status gateway-hub
sudo systemctl status nginx

echo "🎉 Deployment complete!"
echo "API: https://$domain/api/v1"
echo "Health: https://$domain/health"
