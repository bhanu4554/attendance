# Deployment Checklist - AI-Powered Smart Attendance System

Complete checklist for deploying the system to production.

## 🚀 Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Python 3.8+ installed on server
- [ ] Node.js 18+ installed on server
- [ ] PostgreSQL 13+ installed and configured
- [ ] Redis server installed and running
- [ ] Nginx installed for reverse proxy
- [ ] SSL certificates obtained (Let's Encrypt recommended)
- [ ] Domain name configured and pointing to server

### ✅ Database Preparation
- [ ] PostgreSQL database created
- [ ] Database user created with appropriate permissions
- [ ] Database connection tested
- [ ] Backup strategy planned
- [ ] Database migrations tested on staging

### ✅ Security Configuration
- [ ] Strong SECRET_KEY generated
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS configured
- [ ] CORS settings configured
- [ ] JWT settings secured
- [ ] File upload limits set
- [ ] Rate limiting configured

### ✅ Application Files
- [ ] Code repository up to date
- [ ] Dependencies documented in requirements.txt
- [ ] Static files collected
- [ ] Media files directory configured
- [ ] Log files directory created
- [ ] Environment variables file created (.env)

## 🔧 Production Configuration

### Environment Variables (.env)
```bash
# Application Settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DB_NAME=attendance_production
DB_USER=attendance_user
DB_PASSWORD=super-secure-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Settings
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email Configuration (if needed)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Storage
MEDIA_URL=/media/
STATIC_URL=/static/
MEDIA_ROOT=/var/www/attendance-system/media
STATIC_ROOT=/var/www/attendance-system/static

# Face Recognition (if enabled)
FACE_RECOGNITION_TOLERANCE=0.6
FACE_RECOGNITION_MODEL=hog
```

### Django Settings Updates
```python
# settings.py production updates
import os
from pathlib import Path

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Database Connection Pooling
DATABASES['default']['CONN_MAX_AGE'] = 60

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/attendance-system/django.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/attendance-system/django_errors.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
```

## 📦 Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application user
sudo useradd --system --shell /bin/bash --home /var/www/attendance-system attendance
sudo mkdir -p /var/www/attendance-system
sudo chown attendance:attendance /var/www/attendance-system
```

### 2. Database Setup
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE attendance_production;
CREATE USER attendance_user WITH PASSWORD 'super-secure-password';
GRANT ALL PRIVILEGES ON DATABASE attendance_production TO attendance_user;
ALTER USER attendance_user CREATEDB;
\q
```

### 3. Application Deployment
```bash
# Switch to application user
sudo -u attendance -i

# Navigate to application directory
cd /var/www/attendance-system

# Clone repository
git clone <your-repository-url> .

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Frontend setup
cd ../frontend
npm install
npm run build --prod

# Create necessary directories
sudo mkdir -p /var/log/attendance-system
sudo chown attendance:attendance /var/log/attendance-system
sudo mkdir -p /var/www/attendance-system/media
sudo chown attendance:attendance /var/www/attendance-system/media
```

### 4. Systemd Service Setup
```bash
# Create systemd service file
sudo tee /etc/systemd/system/attendance-backend.service << EOF
[Unit]
Description=Attendance System Django Backend
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=attendance
Group=attendance
WorkingDirectory=/var/www/attendance-system/backend
Environment=PATH=/var/www/attendance-system/backend/venv/bin
EnvironmentFile=/var/www/attendance-system/backend/.env
ExecStart=/var/www/attendance-system/backend/venv/bin/gunicorn --workers 3 --bind unix:/var/www/attendance-system/backend/gunicorn.sock attendance_system.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable attendance-backend.service
sudo systemctl start attendance-backend.service
sudo systemctl status attendance-backend.service
```

### 5. Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/attendance-system << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Frontend - Angular application
    location / {
        root /var/www/attendance-system/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://unix:/var/www/attendance-system/backend/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for face recognition endpoints
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
    
    # WebSocket connections
    location /ws/ {
        proxy_pass http://unix:/var/www/attendance-system/backend/gunicorn.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket timeout
        proxy_read_timeout 86400;
    }
    
    # Django admin static files
    location /static/ {
        alias /var/www/attendance-system/backend/static/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Media files (face images, etc.)
    location /media/ {
        alias /var/www/attendance-system/backend/media/;
        expires 1y;
        add_header Cache-Control "public";
        
        # Security for face images
        location ~* /media/face_images/ {
            internal;
            expires 1h;
        }
    }
    
    # File upload size limit
    client_max_body_size 10M;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/attendance-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 7. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw status
```

## 📊 Post-Deployment Verification

### ✅ Service Status Checks
```bash
# Check all services are running
sudo systemctl status attendance-backend
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Check application logs
sudo tail -f /var/log/attendance-system/django.log
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### ✅ Application Tests
- [ ] Frontend loads at https://yourdomain.com
- [ ] API endpoints respond at https://yourdomain.com/api/
- [ ] Admin interface accessible at https://yourdomain.com/admin/
- [ ] WebSocket connections working
- [ ] Face recognition endpoints responding (if enabled)
- [ ] Database queries executing properly
- [ ] Static files serving correctly
- [ ] Media file uploads working

### ✅ Security Tests
- [ ] HTTP redirects to HTTPS
- [ ] SSL certificate valid and trusted
- [ ] Security headers present
- [ ] Admin panel requires authentication
- [ ] API endpoints require valid JWT tokens
- [ ] File upload restrictions working
- [ ] Database connections secured

### ✅ Performance Tests
- [ ] Page load times acceptable
- [ ] API response times under 500ms
- [ ] Database queries optimized
- [ ] Static files cached properly
- [ ] WebSocket connections stable
- [ ] Memory usage within limits
- [ ] CPU usage reasonable

## 🔄 Maintenance Tasks

### Daily
- [ ] Check application logs for errors
- [ ] Verify backup completion
- [ ] Monitor system resources

### Weekly
- [ ] Update system packages
- [ ] Review security logs
- [ ] Check disk space usage
- [ ] Verify SSL certificate status

### Monthly
- [ ] Update application dependencies
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Security audit
- [ ] Performance optimization review

## 📋 Backup Strategy

### Database Backup
```bash
# Create backup script
sudo tee /usr/local/bin/backup-attendance-db.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/attendance-system"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR

# Database backup
pg_dump -h localhost -U attendance_user attendance_production | gzip > \$BACKUP_DIR/db_backup_\$DATE.sql.gz

# Media files backup
tar -czf \$BACKUP_DIR/media_backup_\$DATE.tar.gz -C /var/www/attendance-system/backend/media .

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

sudo chmod +x /usr/local/bin/backup-attendance-db.sh

# Create cron job for daily backups
echo "0 2 * * * /usr/local/bin/backup-attendance-db.sh" | sudo crontab -
```

### Application Backup
```bash
# Create application backup script
sudo tee /usr/local/bin/backup-attendance-app.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/attendance-system"
DATE=\$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/attendance-system"

# Application code backup
tar -czf \$BACKUP_DIR/app_backup_\$DATE.tar.gz -C \$APP_DIR --exclude='venv' --exclude='node_modules' --exclude='*.pyc' --exclude='__pycache__' .

echo "Application backup completed: \$DATE"
EOF

sudo chmod +x /usr/local/bin/backup-attendance-app.sh
```

## 🚨 Rollback Plan

### Quick Rollback Steps
```bash
# 1. Stop services
sudo systemctl stop attendance-backend
sudo systemctl stop nginx

# 2. Restore database from backup
gunzip -c /var/backups/attendance-system/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U attendance_user attendance_production

# 3. Restore application code
cd /var/www/attendance-system
tar -xzf /var/backups/attendance-system/app_backup_YYYYMMDD_HHMMSS.tar.gz

# 4. Restart services
sudo systemctl start attendance-backend
sudo systemctl start nginx

# 5. Verify functionality
curl -I https://yourdomain.com
```

## 📞 Support Contacts

- **System Administrator**: [admin@yourdomain.com]
- **Development Team**: [dev-team@yourdomain.com]
- **Emergency Contact**: [emergency@yourdomain.com]

## 📚 Additional Resources

- **Django Production Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Nginx Configuration**: https://nginx.org/en/docs/
- **PostgreSQL Administration**: https://www.postgresql.org/docs/
- **Let's Encrypt**: https://letsencrypt.org/docs/
- **Redis Configuration**: https://redis.io/documentation

---

**🎉 Deployment Complete!**

Your AI-Powered Smart Attendance System is now live and ready for production use. Monitor the system regularly and follow the maintenance schedule to ensure optimal performance.