# Deployment Guide

## 🚀 Quick Start

### Local Development

```bash
# 1. Navigate to directory
cd fastapi_architecture

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the application
python main.py
```

Access the application:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **Dashboard**: http://localhost:8000

---

## 🐳 Docker Deployment

### Single Container

```bash
# Build image
docker build -t options-dashboard-api .

# Run container
docker run -d \
  --name options-api \
  -p 8000:8000 \
  -v $(pwd)/../live_data:/app/live_data \
  -v $(pwd)/../processed:/app/processed \
  options-dashboard-api
```

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🌐 Production Deployment

### Option 1: Systemd Service

1. **Create service file**: `/etc/systemd/system/options-api.service`

```ini
[Unit]
Description=Options Dashboard FastAPI
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/options-dashboard/fastapi_architecture
Environment="PATH=/opt/options-dashboard/venv/bin"
ExecStart=/opt/options-dashboard/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable options-api
sudo systemctl start options-api
sudo systemctl status options-api
```

### Option 2: Nginx + Uvicorn

1. **Install Nginx**:
```bash
sudo apt install nginx
```

2. **Configure Nginx**: `/etc/nginx/sites-available/options-api`

```nginx
upstream options_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    # Static files
    location /static {
        alias /opt/options-dashboard/static;
        expires 30d;
    }

    # API
    location / {
        proxy_pass http://options_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/options-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 3: Gunicorn + Uvicorn Workers

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

---

## ☁️ Cloud Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH into instance
ssh -i key.pem ubuntu@ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 4. Clone/upload code
# 5. Follow systemd + nginx setup above

# 6. Configure security group
# Allow inbound: 80 (HTTP), 443 (HTTPS), 22 (SSH)
```

### Heroku

```bash
# 1. Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 2. Deploy
heroku create options-dashboard-api
git push heroku main
```

### DigitalOcean App Platform

```yaml
# app.yaml
name: options-dashboard-api
services:
  - name: api
    github:
      repo: your-repo/options-dashboard
      branch: main
      deploy_on_push: true
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8080
    envs:
      - key: LIVE_DATA_DIR
        value: /data/live_data
    http_port: 8080
```

### Railway

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up
```

---

## 🔒 SSL/HTTPS Setup

### Using Certbot (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 📊 Monitoring & Logging

### Application Logs

```bash
# Systemd logs
sudo journalctl -u options-api -f

# Docker logs
docker logs -f options-api

# File logs
tail -f /var/log/options-api/app.log
```

### Health Monitoring

```bash
# Check health endpoint
curl http://localhost:8000/health

# Monitor with cron
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart options-api
```

### Performance Monitoring

Install monitoring tools:
```bash
# Prometheus + Grafana
# New Relic
# DataDog
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

`.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/options-dashboard/fastapi_architecture
            git pull
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart options-api
```

---

## 🔧 Environment Variables

### Production Settings

```env
# .env.production
APP_NAME="Options Dashboard API"
VERSION="1.0.0"
DEBUG=False

HOST=0.0.0.0
PORT=8000

LIVE_DATA_DIR=/data/live_data
PROCESSED_DIR=/data/processed

# CORS (restrict in production)
ALLOWED_ORIGINS=["https://your-domain.com"]

# Workers
WORKERS=4
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Multiple instances behind load balancer
# AWS ELB, Nginx load balancer, HAProxy

upstream backend {
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}
```

### Vertical Scaling

```bash
# Increase workers based on CPU cores
workers = (2 * cpu_cores) + 1

# Example: 4 cores = 9 workers
uvicorn main:app --workers 9
```

---

## 🛡️ Security Checklist

- [ ] Change default ports
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (ufw/iptables)
- [ ] Restrict CORS origins
- [ ] Add rate limiting
- [ ] Regular security updates
- [ ] Backup data regularly
- [ ] Monitor logs for suspicious activity

---

## 🔄 Backup Strategy

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz \
  processed/ \
  live_data/ \
  .env

# Upload to S3/backup server
```

---

## 📞 Support

For deployment issues:
1. Check logs
2. Verify environment variables
3. Test health endpoint
4. Review firewall rules
5. Check disk space

---

**Deployment completed successfully! 🎉**
