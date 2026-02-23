# Phase 1: Project Foundation + Auth + Elasticsearch Connection

> **Goal:** A working web app where a PM can sign up, log in, and see an empty dashboard. The FastAPI backend connects to Elasticsearch. Docker Compose starts everything with one command. The foundation is solid so every future phase builds on it without rework.
>
> **Done means:** docker compose up starts the React frontend, FastAPI backend, and connects to Elastic Cloud. A PM can sign up with email/password, log in, see an empty dashboard with the left sidebar and agent chat bubble visible. The backend can read/write to Elasticsearch. JWT auth protects all API routes. Multi-tenant org_id isolation is in place from day one.

---

## Context for the AI Agent

This is Phase 1 of 8. Nothing exists yet — you are starting from scratch.

You are building Context Engine v2 — a feedback intelligence platform for Product Managers. The full product vision is in PROJECT.md. The complete user experience is in UX.md. Read both before starting.

This phase creates the skeleton: project structure, Docker setup, database connection (Elasticsearch), auth system, and the app shell (sidebar, empty pages, agent chat bubble).

Read .cursorrules before starting. All naming, file size, error handling, logging, and testing rules apply.

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Docker Compose | One command starts frontend + backend. ES + Kibana are on Elastic Cloud (not local). |
| FastAPI backend | Python API server with JWT auth, ES client, health checks. |
| React frontend | App shell with left sidebar, dark theme, empty page stubs, agent chat bubble. |
| Auth system | Sign up, log in, JWT tokens, org-based multi-tenancy. |
| ES connection | Singleton client connected to Elastic Cloud, verified with health check. |

---

## Project Structure

```
context-engine-v2/
├── docker-compose.yml
├── .env.example
├── .env                          # Never committed
├── .gitignore
├── README.md
├── PROJECT.md
├── UX.md
├── TASKS.md
├── LICENSE                       # MIT
├── .cursor/rules/                # Cursor rule files
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app, CORS, middleware, router includes
│   │   ├── config.py             # Settings from env vars (pydantic BaseSettings)
│   │   ├── es_client.py          # Elasticsearch singleton
│   │   ├── dependencies.py       # FastAPI dependencies (get_current_user, get_es_client)
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py           # User + Organization ES document models
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Login/signup request/response schemas
│   │   │   └── common.py         # Shared response shapes
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # /api/v1/auth/* endpoints
│   │   │   └── health.py         # /api/v1/health endpoint
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py   # Signup, login, JWT, password hashing
│   │   │   └── es_service.py     # Low-level ES operations
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── security.py       # JWT encode/decode, password hash/verify
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── public/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── AppLayout.tsx
│   │   │   │   └── ThemeToggle.tsx
│   │   │   ├── agent/
│   │   │   │   └── AgentChatBubble.tsx
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── EmptyState.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── FeedbackPage.tsx
│   │   │   ├── CustomersPage.tsx
│   │   │   ├── SpecsPage.tsx
│   │   │   ├── AnalyticsPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useTheme.ts
│   │   │
│   │   ├── services/
│   │   │   └── api.ts
│   │   │
│   │   ├── types/
│   │   │   ├── auth.ts
│   │   │   └── common.ts
│   │   │
│   │   └── utils/
│   │       └── constants.ts
│
└── docs/
    ├── PHASE_1_SPEC.md
    └── architecture.md
```

---

## Dependencies

### Backend (requirements.txt)

| Package | Purpose |
|---------|---------|
| fastapi>=0.109.0 | Web framework |
| uvicorn[standard]>=0.27.0 | ASGI server |
| elasticsearch[async]>=8.12.0 | Elasticsearch client |
| python-dotenv>=1.0.0 | Load .env files |
| pydantic>=2.5.0 | Data validation |
| pydantic-settings>=2.1.0 | BaseSettings for config |
| python-jose[cryptography]>=3.3.0 | JWT encode/decode |
| passlib[bcrypt]>=1.7.4 | Password hashing |
| python-multipart>=0.0.6 | Form data parsing |
| httpx>=0.26.0 | Async HTTP client |
| pytest>=7.4.0 | Testing |
| pytest-asyncio>=0.23.0 | Async test support |

### Frontend (package.json)

| Package | Purpose |
|---------|---------|
| react>=18.2.0 | UI library |
| react-dom>=18.2.0 | DOM rendering |
| react-router-dom>=6.21.0 | Routing |
| typescript>=5.3.0 | Type safety |
| tailwindcss>=3.4.0 | Styling |
| axios>=1.6.0 | HTTP client |
| lucide-react>=0.300.0 | Icons |
| vite>=5.0.0 | Build tool |

---

## Environment Variables (.env.example)

```
# Elasticsearch (Elastic Cloud)
ELASTICSEARCH_CLOUD_ID=your-deployment:base64string
ELASTICSEARCH_API_KEY=your-api-key

# Auth
JWT_SECRET_KEY=change-this-to-a-random-64-char-string
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Backend
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
API_V1_PREFIX=/api/v1

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Docker Compose (docker-compose.yml)

Two services. ES and Kibana are on Elastic Cloud — NOT local.

**backend:**
- Build: ./backend
- Port: 8000
- Env: .env file
- Volume: ./backend/app mounted for hot reload
- Command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
- Healthcheck: curl http://localhost:8000/api/v1/health

**frontend:**
- Build: ./frontend
- Port: 3000 (or 5173 for Vite)
- Depends on: backend
- Volume: ./frontend/src mounted for hot reload
- Env: VITE_API_BASE_URL=http://localhost:8000/api/v1

### Backend Dockerfile
```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Frontend Dockerfile
```
FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

---

## Elasticsearch Setup

### Connection (es_client.py)

Singleton Elasticsearch client:
- Uses cloud_id + api_key from settings
- get_es_client() returns the singleton
- check_es_health() calls client.info(), returns cluster name + status + version
- If credentials missing: raise clear error on startup
- If connection fails: return degraded status, don't crash app
- Log connection success with cluster name on startup

### Indexes Created on Startup

**users index:**
| Field | ES Type | Purpose |
|-------|---------|---------|
| user_id | keyword | UUID, unique |
| org_id | keyword | Multi-tenancy |
| email | keyword | Login, unique per org |
| hashed_password | keyword | bcrypt hash |
| full_name | text + keyword | Display name |
| role | keyword | "pm" only for now |
| created_at | date | ISO 8601 |
| updated_at | date | ISO 8601 |

**organizations index:**
| Field | ES Type | Purpose |
|-------|---------|---------|
| org_id | keyword | UUID, unique |
| name | text + keyword | Org display name |
| created_at | date | ISO 8601 |
| updated_at | date | ISO 8601 |

Note: No PostgreSQL. Entire system runs on Elasticsearch.

### es_service.py Functions
- ensure_index_exists(index_name, mappings) — Create if missing
- setup_initial_indexes() — Create users + organizations indexes
- index_document(index, doc_id, body) — Store a document
- get_document(index, doc_id) — Get by ID
- search_documents(index, query, size) — Run search
- delete_document(index, doc_id) — Delete by ID

Call setup_initial_indexes() on FastAPI startup event.

---

## Auth System

### POST /api/v1/auth/signup

Request: { email, password, full_name, org_name }
1. Validate email format, password min 8 chars
2. Check email not already in users index → 409 if exists
3. Create org in organizations index (new UUID)
4. Hash password with bcrypt
5. Create user in users index with org_id
6. Generate JWT
7. Return { data: { user: {...}, access_token, token_type: "bearer" } }

### POST /api/v1/auth/login

Request: { email, password }
1. Find user by email
2. Not found → 401 "Invalid email or password"
3. Verify password
4. Wrong → 401 same message
5. Generate JWT with payload: { sub: user_id, org_id, email, exp }
6. Return same shape as signup

### GET /api/v1/auth/me

- Requires Bearer token
- Decode, fetch user from ES
- Return user info (no token)

### JWT Details
- Algorithm: HS256
- Expiry: 1440 min (24 hours)
- Payload: { sub: user_id, org_id, email, exp }
- Header: Authorization: Bearer <token>

### Auth Dependency (dependencies.py)
- get_current_user extracts token, decodes, returns CurrentUser(user_id, org_id, email)
- Missing token → 401
- Invalid/expired → 401

---

## API Endpoints Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | No | ES status + cluster info |
| POST | /auth/signup | No | Create account + org |
| POST | /auth/login | No | Login, get JWT |
| GET | /auth/me | Yes | Current user info |

### Health Response (connected)
```json
{ "status": "healthy", "elasticsearch": { "status": "connected", "cluster_name": "...", "version": "8.x" }, "version": "0.1.0" }
```

### Health Response (disconnected)
```json
{ "status": "degraded", "elasticsearch": { "status": "disconnected", "error": "..." }, "version": "0.1.0" }
```

---

## Schemas (Pydantic)

### schemas/auth.py
- SignupRequest — email (EmailStr), password (min 8), full_name (str), org_name (str)
- LoginRequest — email (EmailStr), password (str)
- UserResponse — user_id, email, full_name, org_id, org_name, role
- AuthResponse — user (UserResponse), access_token (str), token_type (str)

### schemas/common.py
- HealthResponse — status, elasticsearch (dict), version
- ErrorResponse — detail, status_code

---

## Frontend

### Theme
- Dark mode default via Tailwind class strategy
- Dark: gray-950 bg, gray-900 sidebar, gray-800 cards, gray-100 text, blue-500 accent
- Light: white bg, gray-50 sidebar, white cards, gray-900 text, blue-600 accent
- Toggle saves to localStorage

### Sidebar (Sidebar.tsx)
Width: 240px expanded, 64px collapsed.

Nav items:
- Dashboard (LayoutDashboard icon) → /dashboard
- Feedback (MessageSquare icon) → /feedback
- Customers (Users icon) → /customers
- Specs (FileText icon) → /specs
- Analytics (BarChart3 icon) → /analytics

Bottom:
- Settings (Settings icon) → /settings
- Theme toggle (Moon/Sun)
- User (avatar + name) → dropdown: logout

Active: accent bg + white text. Hover: subtle bg.

### Agent Chat Bubble (AgentChatBubble.tsx)
Phase 1: visual only.
- Floating circle, bottom-right (24px from edges)
- Accent color, bot icon
- Click: shows panel (400px wide) with "Agent chat coming soon"

### App Layout (AppLayout.tsx)
Sidebar (240px) + content area (flex-1) + floating agent bubble.

### Pages (all empty states)
- DashboardPage: "No data yet. Set up your product and upload feedback."
- FeedbackPage: "No feedback yet. Import data to start analyzing."
- CustomersPage: "No customers yet. Upload data to connect feedback to revenue."
- SpecsPage: "No specs yet. Ask the agent to create your first spec."
- AnalyticsPage: "Dashboards appear once you have feedback data."
- SettingsPage: tabs (Product Wizard | Data Upload | Connectors | Account | Elasticsearch). Account shows email + theme toggle. Elasticsearch shows /health status. Others show "Coming in Phase X."

### Router (App.tsx)
- /login → LoginPage (public)
- /signup → SignupPage (public)
- /dashboard → DashboardPage (protected)
- /feedback → FeedbackPage (protected)
- /customers → CustomersPage (protected)
- /specs → SpecsPage (protected)
- /analytics → AnalyticsPage (protected)
- /settings → SettingsPage (protected)
- / → redirect to /dashboard or /login

### Auth Hook (useAuth.ts)
- user, isAuthenticated, login(), signup(), logout(), loading
- JWT in localStorage (key: ce_access_token)
- On mount: check token, fetch /auth/me

### API Service (api.ts)
- Axios with baseURL from VITE_API_BASE_URL
- Request interceptor: adds Bearer token
- Response interceptor: 401 → clear token, redirect /login

---

## Testing

### test_health.py
1. GET /health returns 200 with ES info.
2. GET /health returns degraded when ES unreachable.

### test_auth_service.py
1. Signup creates user + org, returns token.
2. Signup duplicate email → 409.
3. Login correct → token.
4. Login wrong password → 401.
5. Login nonexistent email → 401.
6. Password is hashed not plain.
7. JWT payload correct.
8. Expired JWT rejected.

### test_auth_routes.py
1. POST /auth/signup valid → 201.
2. POST /auth/signup short password → 422.
3. POST /auth/signup bad email → 422.
4. POST /auth/signup duplicate → 409.
5. POST /auth/login valid → 200.
6. POST /auth/login wrong password → 401.
7. GET /auth/me with token → 200.
8. GET /auth/me no token → 401.
9. GET /auth/me expired → 401.

### test_es_service.py
1. ensure_index_exists creates when missing.
2. ensure_index_exists skips when exists.
3. index_document stores correctly.
4. search_documents returns results.

---

## Non-Negotiable Rules

1. Every API response: success { "data": {...} }, error { "detail": "..." }, list { "data": [...], "pagination": {...} }.
2. No hardcoded secrets. Everything from .env.
3. ES indexes auto-created on startup.
4. org_id on every document, every query filters by org_id.
5. JWT on every protected route.
6. Dark mode on every page, no white flash.
7. Sidebar visible on every authenticated page.
8. Agent chat bubble visible on every authenticated page.
9. docker compose up starts everything.
10. Type hints on all backend functions.
11. Docstrings on all backend functions.
12. Logging on startup, ES connection, signup, login, errors.

---

## What NOT to Build

- Product wizard / onboarding (Phase 2)
- Feedback upload or ingestion (Phase 3)
- Customer upload (Phase 3)
- Search functionality (Phase 4)
- Agent tools or chat (Phase 5)
- Spec generation (Phase 6)
- Kibana dashboards (Phase 7)
- Data generation scripts (Phase 3)
- Celery / background jobs (Phase 3)
- Slack connector (future)

---

## Acceptance Criteria

Phase 1 is complete when ALL of these are true:

- [ ] docker compose up starts both backend and frontend without errors
- [ ] Backend connects to Elastic Cloud and logs cluster name on startup
- [ ] GET /api/v1/health returns ES connection status
- [ ] users and organizations indexes auto-created on first startup
- [ ] PM can sign up with email, password, name, org name → gets JWT
- [ ] PM can log in with email + password → gets JWT
- [ ] Duplicate email signup returns 409
- [ ] Wrong password login returns 401
- [ ] GET /auth/me with valid token returns user info
- [ ] GET /auth/me without token returns 401
- [ ] Frontend shows login page at /login
- [ ] Frontend shows signup page at /signup
- [ ] After login, PM sees dashboard with left sidebar
- [ ] Sidebar shows all 6 nav items (Dashboard, Feedback, Customers, Specs, Analytics, Settings)
- [ ] Clicking each nav item loads correct page with empty state
- [ ] Agent chat bubble visible bottom-right on every page
- [ ] Clicking chat bubble shows placeholder panel
- [ ] Dark mode is default
- [ ] Theme toggle switches dark/light
- [ ] Theme preference persists on reload
- [ ] Settings > Elasticsearch shows connection status
- [ ] Logout clears session, redirects to /login
- [ ] All backend tests pass
- [ ] No TypeScript errors in frontend build

---

## How to Give This to Cursor

1. Save this file as docs/PHASE_1_SPEC.md in your project.
2. Make sure PROJECT.md, UX.md, and .cursorrules are in the project root.
3. Open Cursor agent chat and type:

> Read docs/PHASE_1_SPEC.md, PROJECT.md, and UX.md. This is the spec for Phase 1. The .cursorrules file applies. Do NOT start building yet. First, create a detailed implementation plan: list every file you will create, what each contains, the order you will work in, and dependencies between files. Present the full plan and wait for my approval before writing any code.

4. Review the plan. Push back on anything that deviates from this spec.
5. Once approved, tell Cursor to start building.
6. After completion, run through the acceptance criteria.

---

## After Phase 1

Once all acceptance criteria pass, come back for Phase 2: Product Setup Wizard. That phase will add:
- 8-step product wizard (basics, areas, goals, segments, competitors, roadmap, teams, tech stack)
- Product context stored in ES {org_id}-product-context index
- Onboarding flow for first-time users
- Settings > Product Wizard page (same UI, editable anytime)
- Agent system prompt auto-populated with product context
