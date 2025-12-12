# Deployment Guide

This guide covers deploying the Ecommerce Platform to production environments.

## Prerequisites

- Docker and Docker Compose
- A VPS, cloud platform (AWS, DigitalOcean, Heroku, etc.), or Kubernetes cluster
- SSL certificate (recommended for HTTPS)
- PostgreSQL database (or managed service)

## Environment Configuration

### 1. Prepare Environment Variables

Create a `.env` file with production values:

```env
# Database
DATABASE_URL=postgresql+psycopg2://user:password@db.example.com:5432/ecommerce
POSTGRES_PASSWORD=<generate-strong-password>

# Security
SECRET_KEY=<generate-with-python-secrets-module>
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Other
DB_WAIT_TIMEOUT=30
```

## Deployment Options

### Option 1: Docker Compose on VPS (DigitalOcean, AWS EC2, Linode)

#### Setup Steps

1. **SSH into your server**
   ```bash
   ssh root@your-server-ip
   ```

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   docker --version
   ```

3. **Clone repository**
   ```bash
   cd /opt
   git clone https://github.com/your-username/ecommerce-platform.git
   cd ecommerce-platform
   ```

4. **Create production environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   nano .env
   ```

5. **Start services**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
   ```

6. **Verify services**
   ```bash
   docker-compose ps
   docker-compose logs -f backend
   ```

#### Nginx Reverse Proxy (Optional but Recommended)

Install Nginx to proxy requests:

```bash
apt-get update
apt-get install nginx
```

Create `/etc/nginx/sites-available/ecommerce`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:5173;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # API endpoints
    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger/OpenAPI docs
    location /docs {
        proxy_pass http://backend/docs;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://backend/redoc;
        proxy_set_header Host $host;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:

```bash
ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### SSL with Certbot (Let's Encrypt)

```bash
apt-get install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 2: Heroku Deployment

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Steps

1. **Create Heroku apps**
   ```bash
   heroku create your-app-name-backend
   heroku create your-app-name-frontend
   ```

2. **Add PostgreSQL addon to backend**
   ```bash
   heroku addons:create heroku-postgresql:standard-0 -a your-app-name-backend
   ```

3. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY="<generated-secret>" -a your-app-name-backend
   heroku config:set CORS_ORIGINS="https://your-app-name-frontend.herokuapp.com" -a your-app-name-backend
   ```

4. **Deploy backend**
   ```bash
   git subtree push --prefix backend heroku main
   ```

5. **Deploy frontend**
   ```bash
   git subtree push --prefix frontend heroku-frontend main
   ```

6. **Run migrations**
   ```bash
   heroku run python backend/migrate.py -a your-app-name-backend
   ```

### Option 3: AWS Elastic Container Service (ECS)

#### Create ECR Repository

```bash
aws ecr create-repository --repository-name ecommerce-backend
aws ecr create-repository --repository-name ecommerce-frontend
```

#### Build and Push Images

```bash
# Backend
docker build -t ecommerce-backend backend/
docker tag ecommerce-backend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/ecommerce-backend:latest
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/ecommerce-backend:latest

# Frontend
docker build -t ecommerce-frontend frontend/
docker tag ecommerce-frontend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/ecommerce-frontend:latest
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/ecommerce-frontend:latest
```

#### Create ECS Task Definition

See [AWS ECS Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-service.html).

### Option 4: Kubernetes (GKE, EKS, AKS)

#### Create Helm Chart (Optional)

```bash
helm create ecommerce
```

#### Deploy

```bash
# Backend
kubectl create secret generic ecommerce-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=secret-key=...

# Frontend
kubectl apply -f frontend-deployment.yaml
kubectl apply -f backend-deployment.yaml
```

See [Kubernetes Documentation](https://kubernetes.io/docs/tasks/run-application/) for detailed setup.

## Database Management

### RDS (Amazon Relational Database Service)

```bash
# Create RDS instance via AWS Console or CLI
aws rds create-db-instance \
  --db-instance-identifier ecommerce-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --allocated-storage 20
```

### Google Cloud SQL

```bash
gcloud sql instances create ecommerce-db \
  --database-version POSTGRES_15 \
  --region us-central1 \
  --tier db-f1-micro
```

### Azure Database for PostgreSQL

Similar process via Azure Portal or CLI.

### Configure Application

Update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

Run migrations:

```bash
python backend/migrate.py
```

## Monitoring and Logging

### Docker Container Logs

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Tail specific number of lines
docker-compose logs -f --tail=50 backend
```

### Cloud Provider Logging

- **AWS**: CloudWatch Logs
- **Google Cloud**: Cloud Logging
- **Azure**: Azure Monitor

### Health Checks

Backend provides a health endpoint:

```bash
curl https://yourdomain.com/health
```

Set up monitoring alerts on this endpoint.

## Backup Strategy

### Database Backups

#### PostgreSQL Pg_dump

```bash
# Backup
pg_dump -h localhost -U postgres -d ecommerce > backup.sql

# Restore
psql -h localhost -U postgres -d ecommerce < backup.sql
```

#### Automated Backups (Docker)

Add to docker-compose.yml:

```yaml
backup:
  image: postgres:15
  environment:
    PGPASSWORD: ${POSTGRES_PASSWORD}
  volumes:
    - ./backups:/backups
  command: >
    sh -c 'while true; do
      pg_dump -h db -U postgres ecommerce > /backups/backup-$(date +%Y%m%d-%H%M%S).sql;
      sleep 86400;
    done'
  depends_on:
    - db
```

## Performance Optimization

### Frontend Build Optimization

```bash
# Production build
npm run build

# Check bundle size
npm run build -- --report
```

### Backend Optimization

- Use connection pooling (SQLAlchemy built-in)
- Cache database queries with Redis (optional)
- Use CDN for static assets

### Database Optimization

```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);
```

## Security Checklist

- [ ] Change SECRET_KEY to a random value
- [ ] Use strong database password
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure CORS_ORIGINS to specific domains
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Use environment variables for secrets (no hardcoding)
- [ ] Keep dependencies updated
- [ ] Enable container scanning (ECR, Docker Hub)
- [ ] Set up database encryption
- [ ] Use managed secrets service (AWS Secrets Manager, etc.)

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection: check DATABASE_URL and POSTGRES_PASSWORD
# - Port already in use: change port mapping in docker-compose.yml
# - Missing migrations: run `docker-compose exec backend python migrate.py`
```

### Frontend can't reach backend

```bash
# Check CORS configuration
# Ensure CORS_ORIGINS includes frontend domain

# Verify API URL in frontend
echo $VITE_API_URL

# Test API from frontend container
curl http://backend:8000/health
```

### Database issues

```bash
# Connect to database
docker-compose exec db psql -U postgres -d ecommerce

# Check migrations
docker-compose exec backend alembic current

# Reset database (development only!)
docker-compose exec db dropdb -U postgres ecommerce
docker-compose exec backend python migrate.py
```

## Scaling

### Horizontal Scaling (Multiple Backend Instances)

With load balancer:

```yaml
services:
  backend-1:
    build: ./backend
  backend-2:
    build: ./backend
  backend-3:
    build: ./backend

  nginx:
    image: nginx:latest
    ports:
      - "8000:8000"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Database Connection Pooling

SQLAlchemy handles connection pooling automatically. For large deployments, consider:

- PgBouncer for connection pooling
- Read replicas for scaling read operations
- Partitioning for large tables

## Cost Optimization

- Use spot instances/preemptible VMs for non-critical workloads
- Enable auto-scaling
- Use managed services (RDS, Cloud SQL) for database
- Implement caching layers
- Compress assets in transit
- Monitor and optimize resource usage

## Additional Resources

- [Docker Production Checklist](https://docs.docker.com/develop/production/)
- [PostgreSQL Deployment Guide](https://www.postgresql.org/docs/current/install.html)
- [OWASP Security Guidelines](https://owasp.org/www-project-secure-coding-practices/)
