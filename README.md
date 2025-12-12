# Ecommerce Platform

A modern, full-stack ecommerce platform built with FastAPI, React, SQLAlchemy, and Docker.

[![CI](https://github.com/your-organization/ecommerce-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/your-organization/ecommerce-platform/actions)
[![Coverage](https://codecov.io/gh/your-organization/ecommerce-platform/branch/main/graph/badge.svg)](https://codecov.io/gh/your-organization/ecommerce-platform)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                 │
│  - Login component with JWT authentication                  │
│  - Product listing and filtering                            │
│  - Shopping cart with persistent storage                    │
│  - Responsive design with WCAG AA accessibility             │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│  - User authentication with JWT tokens                      │
│  - Product CRUD operations                                  │
│  - Shopping cart management                                 │
│  - OpenAPI/Swagger documentation at /docs                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ SQL
┌─────────────────▼───────────────────────────────────────────┐
│               Database (SQLite/PostgreSQL)                  │
│  - SQLAlchemy ORM for type-safe database access            │
│  - Alembic migrations for version control                  │
│  - Support for development (SQLite) and production (PG)    │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ with async support
- **ORM**: SQLAlchemy 2.0 with declarative models
- **Auth**: JWT tokens with python-jose, password hashing with pbkdf2_sha256
- **Migrations**: Alembic for schema versioning
- **Testing**: pytest with TestClient, Playwright for e2e
- **Database**: SQLite (dev), PostgreSQL 15 (prod/test)
- **Server**: Uvicorn with auto-reload

### Frontend
- **Framework**: React 18 with JSX
- **Build Tool**: Vite 5 with hot module replacement
- **Styling**: Modern CSS with Flexbox/Grid, WCAG AA accessible
- **Testing**: Playwright for end-to-end browser tests
- **Quality**: ESLint + Prettier for code formatting

### DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local stack
- **CI/CD**: GitHub Actions with 4 parallel jobs (backend, frontend, integration, e2e)
- **Database Readiness**: Custom wait-for-db script with retry logic

## 📋 Prerequisites

- **Development**: Python 3.11+, Node.js 18+, Docker + Docker Compose
- **Production**: Docker, environment variables for secrets

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start the full stack (backend + frontend + postgres)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Access:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Option 2: Local Development (Python + Node)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or on Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
python migrate.py

# Start server
uvicorn main:app --reload
# Backend: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional, defaults to localhost:8000)
# Create .env.local if needed:
# VITE_API_URL=http://localhost:8000

# Start dev server
npm run dev
# Frontend: http://localhost:5173
```

## 📖 API Documentation

Once backend is running, visit **http://localhost:8000/docs** for interactive Swagger UI or **http://localhost:8000/redoc** for ReDoc documentation.

### Key Endpoints

#### Authentication
- `POST /auth/register` - Create a new user account
- `POST /auth/login` - Get JWT access token

#### Products (Public)
- `GET /products` - List all products
- `GET /products/{id}` - Get product details

#### Products (Admin)
- `POST /products` - Create product (requires auth)
- `PUT /products/{id}` - Update product (requires auth)
- `DELETE /products/{id}` - Delete product (requires auth)

#### Shopping Cart (Private)
- `GET /cart` - Get user's cart items
- `POST /cart` - Add item to cart
- `DELETE /cart/{item_id}` - Remove item from cart

### Example: Register and Login

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'

# Login (get token)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepass123"

# Response: {"access_token": "eyJ0eXAi...", "token_type": "bearer"}

# Use token to access protected endpoints
curl -X GET http://localhost:8000/cart \
  -H "Authorization: Bearer eyJ0eXAi..."
```

## 🧪 Testing

### Unit Tests (Backend)

```bash
cd backend
pytest tests/test_api.py -v
```

### Pre-commit hooks

Install and enable pre-commit hooks to run `ruff` and `black` automatically on commits:

```bash
pip install pre-commit
pre-commit install
# Run hooks against all files
pre-commit run --all-files
```

### Integration Tests (Backend)

Requires backend running on http://localhost:8000:

```bash
cd backend
pytest tests/test_integration.py -v
```

### End-to-End Tests (Frontend)

Requires full stack running (Docker Compose):

```bash
cd frontend
npm run test:e2e
# Or use playwright UI
npx playwright test --ui
```

### E2E Artifacts in CI

- **Artifacts uploaded:** `playwright-report`, `test-results`, and recorded videos/screenshots.
- **Where to find them:** Open the GitHub Actions run for the workflow and download the `playwright-report` or `playwright-report-run-all-tests` artifacts from the job that ran e2e.

> Note: A pull request has been created to enable and verify Playwright artifact uploads in CI.


### Run All Tests in CI

```bash
# Cross-platform scripts
./scripts/run_all_tests.sh       # Mac/Linux
.\scripts\run_all_tests.ps1    # Windows PowerShell

# Control e2e behavior with env vars (optional):
# Skip e2e: SKIP_E2E=1 ./scripts/run_all_tests.sh
# Force e2e to fail if npm missing: FORCE_E2E=1 ./scripts/run_all_tests.sh
```

Quick runs:

```bash
# Run unit + integration only (skip e2e)
SKIP_E2E=1 ./scripts/run_all_tests.sh

# Force e2e to run and fail if npm missing
FORCE_E2E=1 ./scripts/run_all_tests.sh
```

## 🔧 Environment Variables

### Backend (.env or `backend/.env.example`)

```env
# Database configuration
DATABASE_URL=sqlite:///./ecommerce.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname

# JWT Secret (change in production!)
SECRET_KEY=your-super-secret-key-change-in-production

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database wait timeout (seconds)
DB_WAIT_TIMEOUT=60
```

### Frontend (.env.local or VITE_* env vars)

```env
# Backend API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## 📦 Database Migrations

This project uses Alembic for schema versioning.

### Create a New Migration

```bash
cd backend

# After modifying models.py, generate migration
alembic revision --autogenerate -m "Add new_column to users table"

# Review generated file in alembic/versions/

# Apply migration
python migrate.py
```

### Check Migration Status

```bash
cd backend
alembic current         # Show current database version
alembic history         # Show all applied migrations
```

## 🐳 Docker Deployment

### Build Images

```bash
docker-compose build
```

### Production Stack with PostgreSQL

```bash
# Use both compose files for full production setup
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop stack
docker-compose down
```

### Environment Configuration for Production

Before deploying to production:

1. **Secrets Management**
   ```env
   SECRET_KEY=<generate-new-cryptographically-secure-key>
   POSTGRES_PASSWORD=<strong-db-password>
   ```

2. **CORS Configuration**
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Database**
   ```env
   DATABASE_URL=postgresql+psycopg2://user:password@db:5432/ecommerce
   ```

## 🛠️ Development Workflow

### Code Quality

#### Backend

```bash
cd backend

# Check code with ruff (Python linter)
ruff check .

# Format code with black
black .

# Or use auto-formatting
ruff check . --fix
```

#### Frontend

```bash
cd frontend

# Lint code
npm run lint

# Format code
npm run format
```

## 📝 Project Structure

```
ecommerce-platform/
├── backend/                 # FastAPI application
│   ├── main.py             # App entry point, all endpoints
│   ├── db.py               # SQLAlchemy engine & session
│   ├── models.py           # ORM models (User, Product, CartItem)
│   ├── migrate.py          # Alembic migration runner
│   ├── wait_for_db.py      # Database readiness check
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Container image definition
│   ├── entrypoint.sh       # Container startup script
│   ├── pyproject.toml      # Ruff/Black configuration
│   ├── alembic/            # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 0001_initial.py
│   └── tests/              # Test suite
│       ├── test_api.py     # Unit tests
│       └── test_integration.py # HTTP integration tests
│
├── frontend/               # React application
│   ├── src/
│   │   ├── App.jsx        # Main component with state
│   │   ├── main.jsx       # Vite entry point
│   │   ├── styles.css     # Global styles with a11y
│   │   └── components/    # Reusable components
│   │       ├── Login.jsx
│   │       ├── ProductList.jsx
│   │       └── Cart.jsx
│   ├── e2e/               # End-to-end tests
│   │   └── auth.spec.js   # Playwright tests
│   ├── playwright.config.js # Playwright configuration
│   ├── package.json
│   ├── Dockerfile
│   └── index.html         # HTML entry point
│
├── scripts/               # Helper scripts
│   ├── migrate.sh         # Unix migration runner
│   ├── migrate.ps1        # PowerShell migration runner
│   ├── run_tests.sh       # Unix test runner
│   └── run_tests.ps1      # PowerShell test runner
│
├── docker-compose.yml     # Development stack
├── docker-compose.override.yml # PostgreSQL for prod/test
├── .eslintrc.js           # Frontend linting rules
├── .prettierrc.js         # Code formatting rules
├── .gitignore             # Git exclusions
└── README.md              # This file
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run linters: `npm run lint` (frontend), `ruff check .` (backend)
4. Format code: `npm run format` (frontend), `black .` (backend)
5. Commit: `git commit -m "Add feature description"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
Get-NetTcpConnection -LocalPort 8000  # Windows

# Ensure dependencies are installed
cd backend && pip install -r requirements.txt
```

### Database migration fails

```bash
# Ensure database is reachable
cd backend
python wait_for_db.py

# Check migration status
alembic current

# View recent errors
docker-compose logs db  # If using Docker
```

### Frontend can't reach backend

```bash
# Check CORS configuration in backend .env
# Frontend needs backend URL in VITE_API_URL

# Verify backend is running
curl http://localhost:8000/health
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [Playwright Testing Guide](https://playwright.dev/)

Docker Compose

To run frontend and backend together (development), use Docker Compose:

```bash
docker compose up --build
```

Frontend improvements

The frontend has been refactored into small components under `frontend/src/components` and includes basic validation and styling in `frontend/src/styles.css`.

Windows notes & helpers

PowerShell activation may be blocked by your system policy. To avoid manually activating a venv you can use the included helper scripts in `scripts/`:

- Run Alembic migrations (PowerShell):

```powershell
.\scripts\migrate.ps1
```

- Run backend tests (PowerShell):

```powershell
.\scripts\run_tests.ps1
```

Unix shell equivalents are provided as `scripts/migrate.sh` and `scripts/run_tests.sh`.
