# Deployment Guide - Hướng Dẫn Triển Khai

Tài liệu này hướng dẫn 3 cách để triển khai backend:
1. **Local Development** - Phát triển trên máy local
2. **Docker Compose** - Containerized with MySQL
3. **Production** - Deployment cho production

---

## 1️⃣ Local Development Setup

### Yêu Cầu
- Python 3.9+
- MySQL 5.7+ (running locally)
- Git (optional)

### Các Bước

**Step 1: Clone/Download Project**
```bash
cd d:\Document\CSAT_BMPT\BackEnd
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
```

**Step 3: Activate Environment**
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

**Step 4: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Setup Database**
```bash
mysql -u root -p123456 < setup.sql
```

**Step 6: Start Server**
```bash
python main.py
```

**Access:** http://localhost:8000/docs

---

## 2️⃣ Docker Compose Deployment

### Prerequisites
- Docker Desktop installed
- No local MySQL needed (Docker provides it)

### Quick Start

**1. Start Services**
```bash
docker-compose up -d
```

**2. Check Status**
```bash
docker-compose ps
```

**3. View Logs**
```bash
docker-compose logs -f backend
```

**4. Stop Services**
```bash
docker-compose down
```

**Access:**
- Backend: http://localhost:8000/docs
- MySQL: `mysql -h localhost -u root -p123456`

### Database Backup
```bash
docker exec csat_mysql mysqldump -u root -p123456 user_db > backup.sql
```

### Database Restore
```bash
docker exec -i csat_mysql mysql -u root -p123456 user_db < backup.sql
```

---

## 3️⃣ Production Deployment

### Architecture Overview
```
┌─────────────────┐
│   Nginx/Proxy   │ (Reverse Proxy, SSL/TLS)
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI App    │ (Gunicorn + Uvicorn)
└────────┬────────┘
         │
┌────────▼────────┐
│  MySQL Database │ (RDS or self-hosted)
└─────────────────┘
```

### Option A: Linux Server Deployment

**Prerequisites:**
- Ubuntu 20.04+ server
- Python 3.9+, pip, virtualenv
- MySQL 5.7+ (or AWS RDS)
- Nginx
- Supervisor (for process management)

**1. Server Setup**
```bash
# SSH into server
ssh user@your-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv python3-pip \
                   nginx mysql-client supervisor git
```

**2. Clone Repository**
```bash
cd /var/www
git clone <repo-url> csat-backend
cd csat-backend
```

**3. Setup Python Environment**
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configure Environment**
```bash
# Update .env for production
nano .env
```

Settings:
```env
DATABASE_HOST=your-mysql-server.com
DATABASE_USER=production_user
DATABASE_PASSWORD=secure_password_here
ENV=production
HOST=127.0.0.1
PORT=8000
```

**5. Configure Gunicorn (WSGI Server)**
```bash
# Install gunicorn
pip install gunicorn

# Test run
gunicorn main:app -w 4 -b 127.0.0.1:8000
```

**6. Setup Supervisor (Process Manager)**
```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/csat-backend.conf
```

Add:
```ini
[program:csat-backend]
directory=/var/www/csat-backend
command=/var/www/csat-backend/venv/bin/gunicorn main:app -w 4 -b 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/csat-backend.err.log
stdout_logfile=/var/log/csat-backend.out.log
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start csat-backend
```

**7. Configure Nginx (Reverse Proxy)**
```bash
sudo nano /etc/nginx/sites-available/csat-backend
```

Add:
```nginx
upstream csat_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://csat_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/csat-backend /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**8. SSL/TLS with Let's Encrypt**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**9. Check Status**
```bash
# Check application
curl http://localhost:8000/health

# Check supervisor
sudo supervisorctl status

# Check Nginx
sudo systemctl status nginx

# Check MySQL connection
mysql -h your-mysql-server.com -u production_user -p
```

### Option B: Docker on Cloud (AWS, GCP, DigitalOcean)

**Using Docker Hub / Registry:**
```bash
# Build image
docker build -t csat-backend:latest .

# Tag for registry
docker tag csat-backend:latest your-registry/csat-backend:latest

# Push to registry
docker push your-registry/csat-backend:latest
```

**Deploy on AWS EC2:**
```bash
# Pull and run
docker pull your-registry/csat-backend:latest
docker run -d \
  --name csat-backend \
  -p 8000:8000 \
  -e DATABASE_HOST=your-rds-endpoint \
  -e DATABASE_USER=admin \
  -e DATABASE_PASSWORD=secure_password \
  your-registry/csat-backend:latest
```

### Option C: Kubernetes Deployment

**Create deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: csat-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: csat-backend
  template:
    metadata:
      labels:
        app: csat-backend
    spec:
      containers:
      - name: backend
        image: your-registry/csat-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_HOST
          value: "mysql-service"
        - name: DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl expose deployment csat-backend --type=LoadBalancer --port=80 --target-port=8000
```

---

## 📊 Performance Optimization

### Database Optimization
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_email_hash ON users(email);
CREATE INDEX idx_created_at ON users(created_at);

-- Regular maintenance
OPTIMIZE TABLE users;
ANALYZE TABLE users;
```

### Application Optimization
```python
# In main.py - Add database connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
)
```

### Caching Strategy
Consider adding Redis for:
- User session caching
- Frequently accessed user profiles
- Rate limiting

---

## 🔒 Security Checklist

- [ ] Use HTTPS/SSL in production
- [ ] Set strong database password
- [ ] Enable database backups (daily)
- [ ] Setup firewall rules
- [ ] Monitor logs for suspicious activity
- [ ] Update dependencies regularly
- [ ] Enable rate limiting on API
- [ ] Add authentication (JWT) to sensitive endpoints
- [ ] Use environment variables for secrets
- [ ] Setup DDoS protection (CloudFlare, AWS Shield)
- [ ] Regular security audits
- [ ] Database encryption at rest

---

## 📈 Monitoring & Logging

### Application Monitoring
```bash
# Add monitoring with Prometheus
pip install prometheus-client

# Add to main.py
from prometheus_client import start_http_server
start_http_server(8001)  # Metrics on port 8001
```

### Log Management
```bash
# Centralized logging with ELK Stack
pip install python-logstash-async

# Or use cloud logging (AWS CloudWatch, DigitalOcean Logs)
```

### Health Checks
```bash
# Regular health monitoring
while true; do
    curl -f http://localhost:8000/health || alert
    sleep 60
done
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| **503 Bad Gateway** | Check if backend is running: `supervisor status` |
| **Connection refused** | Verify MySQL credentials and network connectivity |
| **High memory usage** | Increase Gunicorn workers: `-w 2` instead of `-w 4` |
| **Slow queries** | Add database indexes, check slow query log |
| **SSL certificate expired** | Renew: `sudo certbot renew --force-renewal` |

---

**✅ Deployment ready! Choose your deployment method and follow the steps above.**
