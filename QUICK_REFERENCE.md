# Quick Reference Guide

## 🚀 Getting Started

### Option 1: Docker Compose (5 minutes)
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development (10 minutes)
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate  # Unix
# OR: venv\Scripts\activate (Windows)
pip install -r requirements.txt
python migrate.py
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 📚 Documentation Map

| Document | Purpose | Read When |
|----------|---------|-----------|
| [README.md](./README.md) | Complete setup guide | First time setup |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design & diagrams | Understanding structure |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Development workflow | Before coding |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Production deployment | Ready to deploy |
| [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) | Pre-deployment verification | Before going live |
| [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) | Features & overview | Project overview |

## 🔧 Common Commands

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python migrate.py

# Start development server
uvicorn main:app --reload

# Run tests
pytest tests/ -v

# Check code quality
ruff check .
black --check .

# Auto-fix issues
ruff check . --fix
black .

# Check alembic status
alembic current
alembic history

# Create new migration
alembic revision --autogenerate -m "describe change"
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Format code
npm run format

# Run e2e tests
npm run test:e2e

# Preview production build
npm run start
```

### Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute command in container
docker-compose exec backend python migrate.py

# Restart specific service
docker-compose restart backend
```

### Database

```bash
cd backend

# Connect to database (Docker)
docker-compose exec db psql -U postgres -d ecommerce

# Export data
pg_dump -U postgres ecommerce > backup.sql

# Import data
psql -U postgres ecommerce < backup.sql

# Check current migrations
alembic current

# View migration history
alembic history

# Rollback one migration
alembic downgrade -1
```

## 🌐 Key URLs (Development)

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | React app |
| Backend | http://localhost:8000 | FastAPI server |
| Swagger Docs | http://localhost:8000/docs | Interactive API docs |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| Database | localhost:5432 | PostgreSQL (Docker Compose) |

## 🔑 Environment Variables

### Backend (.env or environment)

```env
# Required
DATABASE_URL=sqlite:///./ecommerce.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional
DB_WAIT_TIMEOUT=60
```

### Frontend (.env.local)

```env
# Optional (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Create user account
- `POST /auth/login` - Get JWT token
- `GET /health` - Health check

### Products
- `GET /products` - List all products
- `GET /products/{id}` - Get single product
- `POST /products` - Create product (auth required)
- `PUT /products/{id}` - Update product (auth required)
- `DELETE /products/{id}` - Delete product (auth required)

### Shopping Cart
- `GET /cart` - Get user's cart (auth required)
- `POST /cart` - Add item to cart (auth required)
  ```json
  {"product_id": 1, "quantity": 2}
  ```
- `DELETE /cart/{item_id}` - Remove from cart (auth required)

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema

## 🐛 Debugging

### Backend

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check database
from backend.db import SessionLocal
session = SessionLocal()
users = session.query(User).all()

# Test API
curl -X GET http://localhost:8000/products
```

### Frontend

```javascript
// Browser DevTools
console.log('Debug:', value);

// Check token
console.log(localStorage.getItem('token'));

// Test API call
fetch('http://localhost:8000/products')
  .then(r => r.json())
  .then(data => console.log(data));
```

## 🔐 Security Tips

| Item | Action |
|------|--------|
| **Secrets** | Never commit `.env` file |
| **Passwords** | Change `SECRET_KEY` in production |
| **Database** | Use strong password for PostgreSQL |
| **CORS** | Restrict to specific domains |
| **HTTPS** | Always use in production |
| **Dependencies** | Run `pip install --upgrade -r requirements.txt` monthly |
| **Logs** | Never log passwords or tokens |
| **Tokens** | Expire JWT after reasonable time |

## 📈 Performance

| Component | Target | How to Optimize |
|-----------|--------|-----------------|
| API Response | < 500ms | Database indexing, caching |
| DB Query | < 100ms | SQL optimization, indexing |
| Frontend Build | < 5s | Code splitting, lazy loading |
| Bundle Size | < 500KB | Tree shaking, minification |
| Page Load | < 2s | Image optimization, CDN |

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check port usage
lsof -i :8000  # Mac/Linux

# Check dependencies
pip install -r requirements.txt

# Check database connection
python backend/wait_for_db.py
```

### Frontend can't reach backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS_ORIGINS in .env
# Should include frontend URL

# Browser console for CORS error
# Cross-Origin Request Blocked
```

### Database won't connect
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql postgresql://user:pass@localhost:5432/db

# Docker: check if db is running
docker-compose ps
```

### Tests fail
```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/test_api.py::test_register -v

# Run with coverage
pytest --cov=./ tests/
```

## 📦 Deployment Quick Steps

### VPS (DigitalOcean, AWS EC2, etc.)

1. **SSH to server**
   ```bash
   ssh root@your-ip
   ```

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
   ```

3. **Clone repo**
   ```bash
   cd /opt && git clone https://github.com/you/ecommerce-platform.git
   ```

4. **Configure .env**
   ```bash
   cd ecommerce-platform
   cp .env.example .env
   nano .env  # Edit with production values
   ```

5. **Start services**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
   ```

6. **Verify**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

### Heroku

```bash
heroku create app-name
heroku addons:create heroku-postgresql
heroku config:set SECRET_KEY="new-secret"
git push heroku main
heroku run python backend/migrate.py
```

## 📞 Getting Help

1. **Check docs**: [README.md](./README.md), [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **Review code**: Inline comments in main.py, models.py
3. **Search issues**: GitHub Issues for similar problems
4. **Check tests**: test_api.py shows usage examples
5. **API docs**: http://localhost:8000/docs (interactive)

## 🎯 Common Tasks

### Add a new product
```bash
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "description": "Cool widget", "price": 29.99}'
```

### Add item to cart
```bash
curl -X POST http://localhost:8000/cart \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Get user's cart
```bash
curl -X GET http://localhost:8000/cart \
  -H "Authorization: Bearer <token>"
```

## ⚡ Tips & Tricks

- Use `docker-compose logs -f --tail=50` to see recent logs only
- Vite auto-reloads on file save (frontend)
- FastAPI auto-reloads with `--reload` flag (backend)
- SQLAlchemy relationships auto-load related data
- JWT tokens stored in localStorage (browser DevTools → Storage)
- Swagger docs at /docs shows all endpoints with examples

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
