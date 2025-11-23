# 🚀 Deployment Guide

## Production Deployment Checklist

### 1. Environment Setup

```bash
# Set production environment
export FLASK_ENV=production

# Edit .env for production
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
SESSION_COOKIE_SECURE=True
```

### 2. Database Setup

**Option A: SQLite (Small Scale)**
- Default setup works
- Suitable for <1000 properties

**Option B: PostgreSQL (Recommended for Production)**

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb genealogy_prod

# Update .env
DATABASE_PATH=postgresql://user:password@localhost/genealogy_prod
```

### 3. Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Set:
# bind 127.0.0.1
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 4. Tesseract OCR

```bash
# Install Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Verify installation
tesseract --version
```

### 5. Application Setup

```bash
# Clone repository
git clone <repository-url>
cd geneaology

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup
./setup.sh
```

### 6. Systemd Services

**Create Gunicorn Service**

```bash
sudo nano /etc/systemd/system/genealogy.service
```

```ini
[Unit]
Description=Genealogy Platform Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/geneaology
Environment="PATH=/var/www/geneaology/venv/bin"
ExecStart=/var/www/geneaology/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/geneaology/genealogy.sock \
    --timeout 120 \
    --access-logfile /var/www/geneaology/logs/access.log \
    --error-logfile /var/www/geneaology/logs/error.log \
    app_new:app

[Install]
WantedBy=multi-user.target
```

**Create Celery Worker Service**

```bash
sudo nano /etc/systemd/system/genealogy-celery.service
```

```ini
[Unit]
Description=Genealogy Celery Worker
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/geneaology
Environment="PATH=/var/www/geneaology/venv/bin"
ExecStart=/var/www/geneaology/venv/bin/celery \
    -A celery_app worker \
    --loglevel=info \
    --logfile=/var/www/geneaology/logs/celery.log

[Install]
WantedBy=multi-user.target
```

**Enable and Start Services**

```bash
sudo systemctl daemon-reload
sudo systemctl enable genealogy
sudo systemctl enable genealogy-celery
sudo systemctl start genealogy
sudo systemctl start genealogy-celery
```

### 7. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/genealogy
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unix:/var/www/geneaology/genealogy.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static {
        alias /var/www/geneaology/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable Site**

```bash
sudo ln -s /etc/nginx/sites-available/genealogy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### 9. Firewall Setup

```bash
# Allow HTTP/HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 10. Monitoring & Logging

**Log Rotation**

```bash
sudo nano /etc/logrotate.d/genealogy
```

```
/var/www/geneaology/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload genealogy
    endscript
}
```

**Monitoring Scripts**

```bash
# Check application status
sudo systemctl status genealogy
sudo systemctl status genealogy-celery
sudo systemctl status redis

# View logs
tail -f /var/www/geneaology/logs/access.log
tail -f /var/www/geneaology/logs/error.log
tail -f /var/www/geneaology/logs/celery.log
```

### 11. Backup Strategy

```bash
# Create backup script
sudo nano /usr/local/bin/backup-genealogy.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/genealogy"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp /var/www/geneaology/genealogy.db $BACKUP_DIR/genealogy_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz \
    /var/www/geneaology/uploads \
    /var/www/geneaology/pdf_uploads

# Delete backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /usr/local/bin/backup-genealogy.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
```

```
0 2 * * * /usr/local/bin/backup-genealogy.sh >> /var/log/genealogy-backup.log 2>&1
```

### 12. Security Hardening

```bash
# Restrict file permissions
sudo chown -R www-data:www-data /var/www/geneaology
sudo chmod -R 755 /var/www/geneaology
sudo chmod 600 /var/www/geneaology/.env

# Secure sensitive directories
sudo chmod 700 /var/www/geneaology/uploads
sudo chmod 700 /var/www/geneaology/pdf_uploads
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads pdf_uploads logs

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app_new:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ./uploads:/app/uploads
      - ./pdf_uploads:/app/pdf_uploads
      - ./logs:/app/logs
    depends_on:
      - redis

  celery:
    build: .
    command: celery -A celery_app worker --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ./uploads:/app/uploads
      - ./pdf_uploads:/app/pdf_uploads
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
```

**Deploy with Docker:**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Performance Optimization

### 1. Enable Caching

```python
# config.py
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/1'
```

### 2. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_properties_address ON properties(address);
CREATE INDEX idx_properties_owner ON properties(owner_name);
CREATE INDEX idx_heirs_property ON heirs(property_id);
CREATE INDEX idx_heirs_confidence ON heirs(confidence_score);
```

### 3. Gunicorn Tuning

```bash
# Calculate workers: (2 x CPU cores) + 1
# For 4 cores: --workers 9
gunicorn --workers 9 --worker-class gevent app_new:app
```

### 4. Redis Optimization

```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Troubleshooting

### Common Issues

**1. Application won't start**
```bash
# Check logs
sudo journalctl -u genealogy -f

# Check permissions
sudo ls -la /var/www/geneaology
```

**2. Celery not processing tasks**
```bash
# Restart Celery
sudo systemctl restart genealogy-celery

# Check Redis
redis-cli ping
```

**3. High memory usage**
```bash
# Monitor processes
htop

# Restart services
sudo systemctl restart genealogy
sudo systemctl restart genealogy-celery
```

**4. SSL issues**
```bash
# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## Maintenance

### Regular Tasks

**Daily:**
- Review error logs
- Monitor disk space
- Check backups

**Weekly:**
- Review analytics
- Update dependencies (if needed)
- Test backup restoration

**Monthly:**
- Security updates
- Performance review
- Database optimization

---

**Production is now ready! 🚀**
