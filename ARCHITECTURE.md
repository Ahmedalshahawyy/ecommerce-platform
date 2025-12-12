# Architecture & Workflow Diagrams

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        INTERNET / USERS                          │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────▼───────────────────────────────────┐
│                      NGINX Reverse Proxy                         │
│  (Optional, handles SSL termination & load balancing)            │
└──────┬───────────────────────────┬───────────────────────────────┘
       │ HTTP                       │ HTTP
       ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│   Frontend (React)   │    │   Backend (FastAPI)  │
│   Port 5173          │    │   Port 8000          │
│   - Vite Dev Server  │    │   - Uvicorn Server   │
│   - Components       │    │   - REST API         │
│   - Styling          │    │   - Auth & JWT       │
│   - State Mgmt       │    │   - CORS Headers     │
└──────┬───────────────┘    └──────┬───────────────┘
       │                           │ SQL
       └───────────────────────────┼────────────────────────┐
                                   ▼                        ▼
                        ┌────────────────────────┐ ┌──────────────────┐
                        │  PostgreSQL (Port 5432)│ │ Redis (Optional) │
                        │  - Users               │ │ - Cache          │
                        │  - Products            │ │ - Sessions       │
                        │  - Cart Items          │ │ - Rate Limits    │
                        └────────────────────────┘ └──────────────────┘
```

## Request Flow (User Login Example)

```
User Browser                Backend API            Database
     │                           │                     │
     │──1. POST /auth/login──────▶                     │
     │  (email, password)         │                     │
     │                            │                     │
     │                   2. Query user by email──▶     │
     │                            │◀──Return user──    │
     │                            │                     │
     │                   3. Verify password hash        │
     │                            │                     │
     │                   4. Generate JWT token          │
     │                            │                     │
     │◀───5. Return token─────────│                     │
     │   {access_token, type}     │                     │
     │                            │                     │
     │──6. Store token in localStorage                 │
     │                            │                     │
     │──7. GET /products─────────▶                     │
     │  (Authorization: Bearer <token>)                │
     │                            │                     │
     │                   8. Validate JWT token          │
     │                            │                     │
     │                   9. List products───────▶      │
     │                            │◀──Return products───│
     │                            │                     │
     │◀──10. Return products──────│                     │
     │   [{id, name, price}, ...]                      │
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                       USERS TABLE                           │
├─────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY                      │
│ email (UNIQUE)   │ VARCHAR(255) NOT NULL                    │
│ hashed_password  │ VARCHAR(255) NOT NULL                    │
│ created_at       │ TIMESTAMP DEFAULT NOW()                  │
└─────────────────────────────────────────────────────────────┘
          │                              ▲
          │ (user_id FK)                 │ (relationship)
          ▼                              │
┌─────────────────────────────────────────────────────────────┐
│                   CART_ITEMS TABLE                          │
├─────────────────────────────────────────────────────────────┤
│ id (PK)          │ INTEGER PRIMARY KEY                      │
│ user_id (FK)     │ INTEGER FOREIGN KEY → Users(id)          │
│ product_id (FK)  │ INTEGER FOREIGN KEY → Products(id)       │
│ quantity         │ INTEGER NOT NULL                         │
│ created_at       │ TIMESTAMP DEFAULT NOW()                  │
└─────────────────────────────────────────────────────────────┘
          △                       │ (product_id FK)
          │                       ▼
          │ (relationship)
          │       ┌─────────────────────────────────────────────────────────┐
          └───────│                   PRODUCTS TABLE                        │
                  ├─────────────────────────────────────────────────────────┤
                  │ id (PK)          │ INTEGER PRIMARY KEY                  │
                  │ name             │ VARCHAR(255) NOT NULL                │
                  │ description      │ TEXT                                 │
                  │ price            │ DECIMAL(10, 2) NOT NULL              │
                  │ created_at       │ TIMESTAMP DEFAULT NOW()              │
                  └─────────────────────────────────────────────────────────┘
```

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 Developer Pushes Code                       │
│              (git push to main/develop)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼───────┐
                    │ GitHub Repo  │
                    └──────┬───────┘
                           │ Webhook
    ┌──────────────────────▼──────────────────────┐
    │         GitHub Actions CI/CD                │
    │  ┌────────────┬──────────┬─────────┬─────────┐
    │  │  Backend   │ Frontend │Linting  │Integration
    │  │   Tests    │  Tests   │ Jobs    │  Tests
    │  └────────────┴──────────┴─────────┴─────────┘
    └──────────────────────┬──────────────────────┘
                           │ All checks pass
    ┌──────────────────────▼──────────────────────┐
    │         Build & Push Docker Images          │
    │  ┌─────────────────────────────────────┐    │
    │  │ - Backend Docker Image (ecommerce:1.0)  │
    │  │ - Frontend Docker Image (ecommerce:1.0) │
    │  └─────────────────────────────────────┘    │
    └──────────────────────┬──────────────────────┘
                           │ Docker push
    ┌──────────────────────▼──────────────────────┐
    │        Container Registry (DockerHub,       │
    │        ECR, GCR, ACR)                       │
    └──────────────────────┬──────────────────────┘
                           │ Pull image
    ┌──────────────────────▼──────────────────────┐
    │  Production Environment (VPS / Cloud)       │
    │  ┌──────────────┬──────────────────────┐    │
    │  │   Backend    │   Frontend           │    │
    │  │ (Container)  │  (Container)         │    │
    │  └──────────────┴──────────────────────┘    │
    │  ┌──────────────────────────────────────┐   │
    │  │   PostgreSQL Database (RDS/Cloud SQL)   │
    │  └──────────────────────────────────────┘   │
    └──────────────────────────────────────────────┘
```

## CI/CD Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    PULL REQUEST / PUSH                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
    ┌──────────────────────┴───────────────────────────────┐
    │                                                      │
    ▼                                                      ▼
┌──────────────────────────┐                   ┌──────────────────────────┐
│   BACKEND LINT JOB       │                   │   FRONTEND LINT JOB      │
│ - ruff check             │                   │ - eslint check           │
│ - black --check          │                   │                          │
│ ✅ PASS or ❌ FAIL       │                   │ ✅ PASS or ❌ FAIL      │
└──────────┬───────────────┘                   └──────────┬───────────────┘
           │ if pass                                       │ if pass
           ▼                                               ▼
┌──────────────────────────┐                   ┌──────────────────────────┐
│   BACKEND TEST JOB       │                   │  FRONTEND BUILD JOB      │
│ - pip install deps       │                   │ - npm install            │
│ - pytest tests/          │                   │ - npm run build          │
│ - ✅ PASS or ❌ FAIL    │                   │ - npx playwright install │
└──────────┬───────────────┘                   │ - ✅ PASS or ❌ FAIL    │
           │ if pass                           └──────────┬───────────────┘
           │                                              │ if pass
           └──────────────────┬───────────────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │   INTEGRATION + E2E TEST JOB │
                │ - Start PostgreSQL service   │
                │ - Run migrations             │
                │ - Start backend              │
                │ - Start frontend dev server  │
                │ - Run Playwright tests       │
                │ - ✅ PASS or ❌ FAIL        │
                └──────────────┬───────────────┘
                               │
                    ┌──────────┴──────────┐
                    │ All jobs pass       │
                    ▼                     │
              ┌─────────────┐          │ ❌ FAIL
              │ MERGE OK    │          │
              │ Ready for   │          ▼
              │ deployment  │     ┌─────────────┐
              └─────────────┘     │ BLOCK MERGE │
                                  │ Fix issues  │
                                  └─────────────┘
```

## Component Hierarchy (Frontend)

```
┌──────────────────────────────────────────────┐
│            App.jsx (Root)                    │
│  - User state & token management             │
│  - Cart state                                │
│  - API communication                         │
└──────────────┬───────────────────────────────┘
               │
        ┌──────┴──────┬──────────┬──────────────┐
        │             │          │              │
        ▼             ▼          ▼              ▼
   ┌────────────┐┌────────────┐┌──────────┐┌──────────────┐
   │   Login    ││ProductList ││  Cart    ││Navigation    │
   │Component   ││Component   ││Component ││(if added)    │
   │            ││            ││          │└──────────────┘
   │ - Form     ││ - Product  ││ - Items  │
   │ - Auth     ││   grid     ││ - Totals │
   │ - Error    ││ - Search   ││ - Remove │
   │   handling ││ - Add to   ││   items  │
   │            ││   cart     ││          │
   └────────────┘└────────────┘└──────────┘
```

## State Management Flow (Frontend)

```
User Interaction
      │
      ▼
   Component Event Handler
      │
      ▼
   Validate Input
      │
      ├─ Valid ─────────┬─────────────────┐
      │                 │                 │
      │            API Call         localStorage
      │                 │                 │
      │          ┌──────▼──────┐         │
      │          │ fetch/axios │         │
      │          └──────┬──────┘         │
      │                 │                 │
      │          ┌──────▼──────┐         │
      │          │Backend API  │         │
      │          └──────┬──────┘         │
      │                 │                 │
      │          ┌──────▼──────┐         │
      │          │   Response  │         │
      │          └──────┬──────┘         │
      │                 │                 │
      └─────────┬───────┴────────────────┘
                │
                ▼
            setState()
                │
                ▼
          Re-render
                │
                ▼
         User sees update
      │
      └─ Invalid ──────────┐
                           │
                     Show error
```

---

These diagrams provide a visual understanding of the system architecture, deployment flow, CI/CD pipeline, and data structures. Use them for documentation, team onboarding, and presentation purposes.
