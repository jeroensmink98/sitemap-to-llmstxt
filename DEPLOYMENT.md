# 🚀 Deployment Guide - Sitemap to LLMS.txt (Caddy Edition)

This guide explains how to deploy the application on your Docker server using **Caddy** for automatic SSL/TLS management.

## 🐳 **Docker Deployment with Caddy (Recommended)**

### **Why Caddy?**
- **Automatic HTTPS**: Zero-config SSL certificates with Let's Encrypt
- **Simpler than Nginx**: Clean, readable configuration
- **Built-in security**: Modern TLS defaults and security headers
- **Auto-renewal**: Certificates automatically renew every 60 days
- **Performance**: Fast, lightweight, and efficient

### **Prerequisites**
- Docker and Docker Compose installed on your server
- At least 2GB RAM available
- Ports 80 (HTTP) and 443 (HTTPS) available
- A domain name pointing to your server IP

### **Quick Start**

1. **Clone the repository on your server:**
```bash
git clone <your-repo-url>
cd sitemap-to-llmstxt
```

2. **Make scripts executable:**
```bash
chmod +x deploy.sh build-frontend.sh
```

3. **Deploy with one command:**
```bash
./deploy.sh
```

The script will:
- Build the frontend automatically
- Ask for your domain name
- Update all configuration files
- Deploy all services with Docker
- Set up automatic SSL/TLS

### **Services Overview**

| Service | Port | Purpose | Container Name |
|---------|------|---------|----------------|
| **Caddy** | 80, 443 | Reverse proxy + SSL + Static files | `llmstxt-caddy` |
| **Backend** | 8000 (internal) | FastAPI + Celery | `llmstxt-backend` |
| **Worker** | - | Background processing | `llmstxt-worker` |
| **Redis** | 6379 | Job queue + cache | `llmstxt-redis` |

### **Architecture**
```
Internet → Port 80/443 → Caddy (SSL + Proxy) → Port 8000 → FastAPI (Backend)
                                    ↓
                              Static Files (Svelte App)
                                    ↓
                              API Proxy to Backend
```

## 🔧 **Configuration Options**

### **Automatic Configuration**
The `deploy.sh` script automatically:
- Updates `docker/Caddyfile` with your domain
- Updates `docker/docker-compose.prod.yml` with your domain
- Creates backups of original files

### **Manual Configuration (Optional)**
If you prefer to configure manually:

#### **1. Update Caddyfile:**
```bash
# Edit docker/Caddyfile
# Replace 'your-domain.com' with your actual domain
```

#### **2. Update Docker Compose:**
```yaml
# Edit docker/docker-compose.prod.yml
environment:
  - DOMAIN=your-domain.com  # Change to your domain
```

### **Environment Variables**
All environment variables are automatically configured by Docker Compose.

## 📁 **File Structure After Deployment**

```
/var/lib/docker/volumes/
├── llmstxt_outputs/          # Generated LLMS.txt files
├── llmstxt_redis_data/       # Redis persistence
├── llmstxt_caddy_data/       # Caddy certificates and data
└── llmstxt_caddy_config/     # Caddy configuration
```

## 🚀 **Production Features**

### **1. Automatic SSL/TLS**
- **Zero configuration** required
- **Let's Encrypt** certificates automatically obtained
- **Auto-renewal** every 60 days
- **HTTP to HTTPS** automatic redirect
- **Modern TLS** defaults (TLS 1.3, strong ciphers)

### **2. Security Features**
- **Rate limiting**: API (10 req/s), General (30 req/s)
- **Security headers**: XSS protection, frame options, content type
- **CORS handling**: Proper cross-origin request handling
- **Request validation**: Input sanitization and validation

### **3. Performance Optimizations**
- **Static file caching**: Long-term caching for assets
- **Gzip compression**: Automatic compression for text files
- **SPA routing**: Proper handling of Svelte routes
- **Load balancing**: Ready for horizontal scaling

## 📊 **Monitoring & Maintenance**

### **Health Checks**
- **Backend**: `https://your-domain.com/api/health`
- **Caddy**: `https://your-domain.com/health`

### **Logs**
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs caddy
docker-compose -f docker-compose.prod.yml logs backend
```

### **Updates**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./deploy.sh
```

## 🔒 **Security Features**

### **Automatic Security**
- **TLS 1.3** by default
- **Strong cipher suites** automatically selected
- **OCSP stapling** for better performance
- **HSTS headers** for additional security

### **Rate Limiting**
- **API endpoints**: 10 requests/second
- **General traffic**: 30 requests/second
- **Burst handling**: Configurable burst limits

### **Security Headers**
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. SSL Certificate Issues**
```bash
# Check Caddy logs
docker-compose -f docker-compose.prod.yml logs caddy

# Verify domain DNS
nslookup your-domain.com

# Check port 80/443 availability
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

#### **2. Frontend Not Loading**
```bash
# Check if frontend is built
ls -la client/dist/

# Rebuild frontend
./build-frontend.sh

# Check Caddy logs
docker-compose -f docker-compose.prod.yml logs caddy
```

#### **3. Backend Connection Issues**
```bash
# Check backend health
curl -f http://localhost:8000/health

# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Verify Redis connection
docker-compose -f docker-compose.prod.yml logs redis
```

### **Debug Mode**
For debugging, run without `-d` flag:
```bash
cd docker
docker-compose -f docker-compose.prod.yml up
```

## 📈 **Scaling**

### **Horizontal Scaling**
```yaml
# Edit docker/docker-compose.prod.yml
worker:
  deploy:
    replicas: 5  # Run 5 worker instances
```

### **Resource Limits**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## 🔄 **Backup & Recovery**

### **Backup Script**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker run --rm -v llmstxt_outputs:/data -v $(pwd):/backup alpine tar czf /backup/outputs_$DATE.tar.gz -C /data .
docker run --rm -v llmstxt_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_$DATE.tar.gz -C /data .
docker run --rm -v llmstxt_caddy_data:/data -v $(pwd):/backup alpine tar czf /backup/caddy_$DATE.tar.gz -C /data .
```

### **Restore**
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore volumes
docker run --rm -v llmstxt_outputs:/data -v $(pwd):/backup alpine tar xzf /backup/outputs_$DATE.tar.gz -C /data
docker run --rm -v llmstxt_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis_$DATE.tar.gz -C /data
docker run --rm -v llmstxt_caddy_data:/data -v $(pwd):/backup alpine tar xzf /backup/caddy_$DATE.tar.gz -C /data

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 **Domain Configuration**

### **DNS Setup**
Point your domain to your server's IP address:
```
A    your-domain.com    →    YOUR_SERVER_IP
```

### **Automatic Configuration**
The `deploy.sh` script automatically updates:
- `docker/Caddyfile` with your domain
- `docker/docker-compose.prod.yml` with your domain

## 📝 **Deployment Checklist**

- [ ] Server has Docker and Docker Compose installed
- [ ] Ports 80 and 443 are available
- [ ] Domain points to server IP
- [ ] Scripts are executable (`chmod +x deploy.sh build-frontend.sh`)
- [ ] Firewall allows HTTP (80) and HTTPS (443)
- [ ] Backup strategy planned

## 🆘 **Support**

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify container status: `docker-compose ps`
3. Check resource usage: `docker stats`
4. Review this documentation
5. Check Caddy logs specifically: `docker-compose logs caddy`

## 🎯 **Benefits of Caddy Setup**

1. **Zero SSL Configuration**: Automatic HTTPS with Let's Encrypt
2. **Simpler Deployment**: One script handles everything
3. **Better Security**: Modern TLS defaults and security headers
4. **Easier Maintenance**: Automatic certificate renewal
5. **Performance**: Fast, lightweight, and efficient
6. **Developer Friendly**: Clean, readable configuration

---

**Happy Deploying with Caddy! 🚀🔐**
