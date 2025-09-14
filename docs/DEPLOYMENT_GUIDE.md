# BuyBuy E-Commerce Deployment Guide

## Deployment Overview

This guide covers deploying the BuyBuy e-commerce backend application using Docker and Kubernetes. The deployment supports both development and production environments with proper scaling, monitoring, and security configurations.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB+ for production)
- **Storage**: 20GB+ available space
- **Network**: Internet connectivity for package downloads

### Required Software

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Kubernetes**: 1.21+ (for production)
- **kubectl**: Latest version
- **MySQL**: 8.0+ (if not using containerized version)
- **Redis**: 6.0+ (if not using containerized version)

## Environment Configuration

### Environment Variables

Create environment files for different deployment stages:

#### Development (.env.dev)

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-for-development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=buybuy_dev
DB_USER=buybuy_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=3306

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=604800

# File Storage
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles

# Email Settings (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=DEBUG
```

#### Production (.env.prod)

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secure-secret-key
ALLOWED_HOSTS=api.buybuy.com,your-domain.com

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=buybuy_prod
DB_USER=buybuy_user
DB_PASSWORD=super-secure-password
DB_HOST=mysql-service
DB_PORT=3306

# Redis
REDIS_URL=redis://redis-service:6379/0

# JWT Settings
JWT_SECRET_KEY=your-super-secure-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=604800

# File Storage
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles
AWS_S3_BUCKET_NAME=your-s3-bucket
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Logging
LOG_LEVEL=INFO
```

## Docker Deployment

### 1. Dockerfile

Create a multi-stage Dockerfile for optimized production builds:

```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "config.wsgi:application"]
```

### 2. Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: buybuy_mysql
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: buybuy_dev
      MYSQL_USER: buybuy_user
      MYSQL_PASSWORD: dev_password
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - '3306:3306'
    volumes:
      - mysql_data:/var/lib/mysql
      - ./docker/mysql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - buybuy_network

  redis:
    image: redis:7-alpine
    container_name: buybuy_redis
    restart: unless-stopped
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data
    networks:
      - buybuy_network

  web:
    build: .
    container_name: buybuy_web
    restart: unless-stopped
    ports:
      - '8000:8000'
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=True
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - buybuy_network
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             python manage.py runserver 0.0.0.0:8000"

  nginx:
    image: nginx:alpine
    container_name: buybuy_nginx
    restart: unless-stopped
    ports:
      - '80:80'
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    networks:
      - buybuy_network

volumes:
  mysql_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  buybuy_network:
    driver: bridge
```

### 3. Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: buybuy_mysql_prod
    restart: always
    environment:
      MYSQL_DATABASE: buybuy_prod
      MYSQL_USER: buybuy_user
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes:
      - mysql_prod_data:/var/lib/mysql
      - ./docker/mysql/my.cnf:/etc/mysql/conf.d/my.cnf
    networks:
      - buybuy_network
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  redis:
    image: redis:7-alpine
    container_name: buybuy_redis_prod
    restart: always
    volumes:
      - redis_prod_data:/data
      - ./docker/redis/redis.conf:/usr/local/etc/redis/redis.conf
    networks:
      - buybuy_network
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  web:
    build: .
    container_name: buybuy_web_prod
    restart: always
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DEBUG=False
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - buybuy_network
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  nginx:
    image: nginx:alpine
    container_name: buybuy_nginx_prod
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./docker/nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/ssl:/etc/nginx/ssl
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    networks:
      - buybuy_network

volumes:
  mysql_prod_data:
  redis_prod_data:
  static_volume:
  media_volume:

networks:
  buybuy_network:
    driver: bridge
```

### 4. Nginx Configuration

```nginx
# docker/nginx/nginx.conf
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name localhost;
    client_max_body_size 20M;

    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /health/ {
        proxy_pass http://django;
        access_log off;
    }
}
```

## Kubernetes Deployment

### 1. Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: buybuy
  labels:
    name: buybuy
```

### 2. ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: buybuy-config
  namespace: buybuy
data:
  DEBUG: 'False'
  DB_ENGINE: 'django.db.backends.mysql'
  DB_NAME: 'buybuy_prod'
  DB_HOST: 'mysql-service'
  DB_PORT: '3306'
  REDIS_URL: 'redis://redis-service:6379/0'
  MEDIA_ROOT: '/app/media'
  STATIC_ROOT: '/app/staticfiles'
  LOG_LEVEL: 'INFO'
```

### 3. Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: buybuy-secrets
  namespace: buybuy
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret-key>
  DB_PASSWORD: <base64-encoded-db-password>
  DB_ROOT_PASSWORD: <base64-encoded-db-root-password>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
  EMAIL_HOST_PASSWORD: <base64-encoded-email-password>
```

### 4. MySQL Deployment

```yaml
# k8s/mysql-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: buybuy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_DATABASE
              valueFrom:
                configMapKeyRef:
                  name: buybuy-config
                  key: DB_NAME
            - name: MYSQL_USER
              value: 'buybuy_user'
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: buybuy-secrets
                  key: DB_PASSWORD
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: buybuy-secrets
                  key: DB_ROOT_PASSWORD
          volumeMounts:
            - name: mysql-storage
              mountPath: /var/lib/mysql
          resources:
            requests:
              memory: '1Gi'
              cpu: '500m'
            limits:
              memory: '2Gi'
              cpu: '1000m'
      volumes:
        - name: mysql-storage
          persistentVolumeClaim:
            claimName: mysql-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: buybuy
spec:
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
  namespace: buybuy
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### 5. Redis Deployment

```yaml
# k8s/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: buybuy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          volumeMounts:
            - name: redis-storage
              mountPath: /data
          resources:
            requests:
              memory: '256Mi'
              cpu: '250m'
            limits:
              memory: '512Mi'
              cpu: '500m'
      volumes:
        - name: redis-storage
          persistentVolumeClaim:
            claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: buybuy
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: buybuy
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### 6. Django Application Deployment

```yaml
# k8s/django-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  namespace: buybuy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
        - name: django
          image: buybuy:latest
          ports:
            - containerPort: 8000
          env:
            - name: DB_USER
              value: 'buybuy_user'
          envFrom:
            - configMapRef:
                name: buybuy-config
            - secretRef:
                name: buybuy-secrets
          volumeMounts:
            - name: media-storage
              mountPath: /app/media
            - name: static-storage
              mountPath: /app/staticfiles
          livenessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              memory: '512Mi'
              cpu: '250m'
            limits:
              memory: '1Gi'
              cpu: '500m'
      volumes:
        - name: media-storage
          persistentVolumeClaim:
            claimName: media-pvc
        - name: static-storage
          persistentVolumeClaim:
            claimName: static-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: django-service
  namespace: buybuy
spec:
  selector:
    app: django-app
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: media-pvc
  namespace: buybuy
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: static-pvc
  namespace: buybuy
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

### 7. Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: buybuy-ingress
  namespace: buybuy
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: 'true'
    nginx.ingress.kubernetes.io/proxy-body-size: '20m'
spec:
  tls:
    - hosts:
        - api.buybuy.com
      secretName: buybuy-tls
  rules:
    - host: api.buybuy.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: django-service
                port:
                  number: 8000
```

## Deployment Commands

### Docker Deployment

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose logs -f web

# Scale services
docker-compose up --scale web=3
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy services
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/django-deployment.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n buybuy
kubectl get services -n buybuy

# View logs
kubectl logs -f deployment/django-app -n buybuy

# Scale deployment
kubectl scale deployment django-app --replicas=5 -n buybuy
```

## Health Checks and Monitoring

### Health Check Endpoint

```python
# In Django views
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    """Health check endpoint for load balancers and monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Check Redis
    try:
        cache.get('health_check')
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
```

### Monitoring Setup

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: buybuy-monitor
  namespace: buybuy
spec:
  selector:
    matchLabels:
      app: django-app
  endpoints:
    - port: 8000
      path: /metrics/
      interval: 30s
```

## Backup and Recovery

### Database Backup

```bash
# Create backup script
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="buybuy_prod"

# Create backup
mysqldump -h mysql-service -u root -p$DB_ROOT_PASSWORD $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### Kubernetes CronJob for Backups

```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: buybuy
spec:
  schedule: '0 2 * * *' # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: mysql:8.0
              command:
                - /bin/bash
                - -c
                - |
                  mysqldump -h mysql-service -u root -p$MYSQL_ROOT_PASSWORD $MYSQL_DATABASE > /backup/backup_$(date +%Y%m%d_%H%M%S).sql
                  gzip /backup/backup_*.sql
              env:
                - name: MYSQL_ROOT_PASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: buybuy-secrets
                      key: DB_ROOT_PASSWORD
                - name: MYSQL_DATABASE
                  valueFrom:
                    configMapKeyRef:
                      name: buybuy-config
                      key: DB_NAME
              volumeMounts:
                - name: backup-storage
                  mountPath: /backup
          volumes:
            - name: backup-storage
              persistentVolumeClaim:
                claimName: backup-pvc
          restartPolicy: OnFailure
```

## Security Considerations

### SSL/TLS Configuration

```nginx
# SSL configuration in nginx
server {
    listen 443 ssl http2;
    server_name api.buybuy.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: buybuy-network-policy
  namespace: buybuy
spec:
  podSelector:
    matchLabels:
      app: django-app
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: mysql
      ports:
        - protocol: TCP
          port: 3306
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**

   ```bash
   # Check database connectivity
   kubectl exec -it deployment/django-app -n buybuy -- python manage.py dbshell
   ```

2. **Pod Startup Issues**

   ```bash
   # Check pod logs
   kubectl logs -f deployment/django-app -n buybuy

   # Check pod events
   kubectl describe pod <pod-name> -n buybuy
   ```

3. **Resource Constraints**
   ```bash
   # Check resource usage
   kubectl top pods -n buybuy
   kubectl top nodes
   ```

### Performance Tuning

1. **Database Optimization**

   - Monitor slow queries
   - Optimize indexes
   - Configure connection pooling

2. **Application Optimization**

   - Enable caching
   - Optimize static file serving
   - Configure gunicorn workers

3. **Infrastructure Optimization**
   - Right-size containers
   - Configure auto-scaling
   - Optimize network policies

## Maintenance

### Regular Maintenance Tasks

1. **Security Updates**

   ```bash
   # Update base images
   docker build --no-cache -t buybuy:latest .
   kubectl set image deployment/django-app django=buybuy:latest -n buybuy
   ```

2. **Database Maintenance**

   ```bash
   # Optimize tables
   kubectl exec -it deployment/mysql -n buybuy -- mysql -u root -p -e "OPTIMIZE TABLE products, categories, users;"
   ```

3. **Log Rotation**
   ```bash
   # Configure log rotation in Kubernetes
   kubectl apply -f k8s/logging-config.yaml
   ```

This deployment guide provides a comprehensive approach to deploying the BuyBuy e-commerce backend with proper scaling, monitoring, and security configurations.
