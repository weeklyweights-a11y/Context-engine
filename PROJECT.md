# PROJECT.md — Context Engine v2

## One-Liner
**Cursor for PMs** — an always-on feedback intelligence platform that monitors customer feedback from every source, detects emerging issues, and generates production-ready engineering specs. Full product. Powered by Elasticsearch.

## What This Is
Context Engine v2 is a **production-grade feedback intelligence platform** for Product Managers. It replaces v1's PostgreSQL + Redis backend with Elasticsearch, gaining native semantic search (ELSER), real-time analytics (ES|QL), and an AI agent (Agent Builder) — while keeping everything that made v1 work: auth, multi-tenancy, custom React frontend, real data ingestion.

It's not a demo. It's a full product that a PM team can actually use.

## How PMs Access It
- **Web app** via browser (localhost:3000 in dev, deployed URL in prod)
- **Setup:** `git clone → cp .env.example .env → docker compose up → open browser`
- Docker runs the React frontend + FastAPI backend
- Elasticsearch + Kibana run on Elastic Cloud (not local)
- PM signs up with email/password, goes through optional onboarding, starts using immediately

## V1 → V2: What Changes, What Stays

### Stays (from v1)
- Custom React frontend
- Auth + multi-tenancy (users, orgs, roles)
- CSV/file upload for real data ingestion
- Full pipeline: ingest → analyze → generate specs
- Production-grade architecture

### Upgraded (Postgres → Elasticsearch)
- PostgreSQL → Elasticsearch (storage, search, analytics — ES is the ONLY datastore)
- pgvector + sentence-transformers → ELSER (native semantic search, zero ML infra)
- Redis cache → Elasticsearch aggregations (real-time, no cache layer)
- Custom SQL queries → ES|QL (pipe-based analytics)
- Ollama local LLM → Elasticsearch Agent Builder (native agent with tools)

### New in v2
- **Always-on monitoring** — Kibana dashboards + React dashboard widgets. PM has both open.
- **Rich product context** — 8-step product wizard: basics, areas, goals, segments/pricing, competitors, roadmap, teams, tech stack. Agent knows ALL of it.
- **Business context layer** — Customer profiles with ARR, renewal dates, health scores. Every insight connects to revenue.
- **11 feedback sources** — App Store, G2, support tickets, NPS, email, Slack, sales calls, internal team, interviews, bug reports, community forums.
- **4-doc spec output** — PRD, Architecture, Rules, Plan. Each standalone, backed by real data, citing real customers and competitors.
- **Proactive intelligence** — Agent detects trends and alerts PMs, not just reactive Q&A.
- **Dual interface** — React frontend for daily workflow + Kibana for deep analytics + Agent chat always available.

## The Problem
PMs drown in feedback from 5+ sources. They manually check dashboards, build spreadsheets, miss patterns. Nobody notices checkout complaints spiked 40% until a customer churns. Nobody connects the Slack message, support ticket, and app store review describing the same problem. Then they spend hours writing PRDs from gut feeling instead of data.

Context Engine v2 closes the loop: raw feedback → monitoring → analysis → business context → 4-doc engineering spec. No other tool does this end-to-end.

---

## User Experience Summary

> Full details in UX.md. Read that file for every screen and interaction.

### User Type
Product Manager — the only user type. Full access to everything.

### App Structure
- **Auth:** Email/password login, JWT-based, multi-tenant orgs
- **Theme:** Dark mode default, light mode toggle
- **Navigation:** Left sidebar with text labels (Jira-style)
- **Agent Chat:** Always-visible floating sidebar panel (Intercom-style), accessible from every page

### Pages (Left Sidebar)
1. **Dashboard** — home page, 9 customizable widgets (summary cards, volume chart, sentiment breakdown, top issues, product area breakdown, at-risk customers, recent feedback, source distribution, segment breakdown)
2. **Feedback** — semantic search + filters, slide-out detail panel with customer card + similar items
3. **Customers** — list with filters, full profile pages (health, revenue, sentiment trend, feedback history, specs mentioning them)
4. **Specs** — saved spec history, 4-tab viewer (PRD | Architecture | Rules | Plan), download, share, edit, regenerate
5. **Analytics** — Kibana dashboards embedded via iframe (overview, trends, deep dive, custom)
6. **Settings** — Product Wizard (8 steps), Data Upload, Connectors, Account, Elasticsearch status

### Onboarding (First Time)
Optional, all steps skippable. Three sections:
1. **Product Wizard** (8 steps): Product basics → Product areas → Business goals → Customer segments + pricing → Competitors → Roadmap → Team structure → Tech stack
2. **Upload Feedback**: CSV + manual entry, auto-detects product areas from content
3. **Upload Customers**: CSV + manual entry, links to segments from wizard

### Agent Chat (Always Available)
- Floating bubble bottom-right, expands to right sidebar panel (~400px)
- 10 capabilities: search, trends, comparison, investigation, prioritization, customer lookup, spec generation, explanation, product context, competitive analysis
- Context-aware: pre-fills queries when opened from dashboard, feedback detail, customer profile
- Knows ALL product context (injected into system prompt from wizard data)
- Generates 4-doc specs, auto-saves to Specs page

### Feedback Sources (11 total)
| Source | Type | Ingestion Now | Future |
|--------|------|---------------|--------|
| App Store Reviews | External | CSV / Manual | Connector |
| G2 / Capterra | External | CSV / Manual | Connector |
| Support Tickets | External | CSV / Manual | Zendesk, Intercom |
| NPS / CSAT Surveys | External | CSV / Manual | Connector |
| Customer Emails | External | CSV / Manual | Connector |
| Sales Call Notes | Internal+External | CSV / Manual | CRM |
| Slack Messages | Internal | CSV / Manual / Connector | Available |
| Internal Team Feedback | Internal | CSV / Manual | Slack |
| User Interviews | Research | CSV / Manual | Connector |
| Bug Reports | Technical | CSV / Manual | Jira, Linear |
| Community / Discord | Community | CSV / Manual | Connector |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                React Frontend (Vite + Tailwind)      │
│  Auth │ Dashboard │ Feedback │ Customers │ Specs │   │
│  Analytics │ Settings │ Agent Chat Panel             │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (axios + JWT)
┌──────────────────────┴──────────────────────────────┐
│              FastAPI Backend (Python 3.11+)           │
│  Auth │ Ingestion │ Search │ Agent Proxy │ Specs     │
│  Product Context │ Customer │ Analytics              │
└──────────────────────┬──────────────────────────────┘
                       │ elasticsearch-py client
┌──────────────────────┴──────────────────────────────┐
│              Elasticsearch (Elastic Cloud)            │
│  users │ organizations │ {org}-feedback │             │
│  {org}-customers │ {org}-product-context │            │
│  {org}-specs                                         │
│  ELSER (semantic) │ ES|QL (analytics)                │
│  Agent Builder (conversational agent)                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              Kibana (Elastic Cloud)                   │
│  Monitoring Dashboards │ Deep Dive │ Agent Playground │
└─────────────────────────────────────────────────────┘
```

### Elasticsearch Indexes

| Index | Purpose | Created When |
|-------|---------|-------------|
| users | User accounts (all orgs) | App startup |
| organizations | Org records | App startup |
| {org_id}-feedback | Feedback items with ELSER embeddings | First feedback upload |
| {org_id}-customers | Customer profiles | First customer upload |
| {org_id}-product-context | Product wizard data (all 8 sections) | Product wizard save |
| {org_id}-specs | Generated spec documents | First spec generation |

No PostgreSQL. Elasticsearch is the only datastore.

### Docker Compose Services
| Service | What | Port |
|---------|------|------|
| backend | FastAPI (Python 3.11) | 8000 |
| frontend | React (Vite) | 3000 |

ES + Kibana run on Elastic Cloud (not in Docker).

---

## The 8 Layers

### Layer 1: Data Ingestion (Multi-Source)
Three data types: product context (wizard), customer profiles, feedback.
Ingestion: CSV upload, manual entry, Slack connector (future: Zendesk, Jira, etc.)
Auto-detection: product areas from feedback text, sentiment analysis on ingest.

### Layer 2: Store + Understand (Elasticsearch)
All data with raw text (keyword) + ELSER embeddings (semantic) + structured fields (filters).
Hybrid search: keyword + semantic for all user-facing queries.
ES|QL for real-time aggregations.

### Layer 3: Monitor + Detect (Dashboard + Kibana)
React dashboard: 9 customizable widgets.
Kibana: 3 pre-built dashboards (overview, trends, deep dive).

### Layer 4: Cluster + Name (Theme Intelligence)
Agent groups feedback into named sub-themes via vector similarity.
Dynamic recalculation as new feedback arrives.

### Layer 5: Compare + Alert (Proactive Intelligence)
Time comparisons, cross-topic ranking, segment analysis.
Every comparison connected to business impact (ARR, renewals).

### Layer 6: Connect to Business Impact
Customer segment revenue, specific account ARR, team ownership, quarterly priorities, severity labels, renewal risk flags.

### Layer 7: Conversational Agent
ES Agent Builder with 7+ tools: search_feedback, trend_analysis, top_issues, find_similar, customer_lookup, compare_segments, generate_spec.
Accessible from React chat panel + Kibana playground + API.

### Layer 8: Generate Specs (4-Doc Output)
PRD, Architecture, Rules, Plan.
Each includes real quotes, real customer names, real ARR, competitor context, team assignments.
Saved to ES, viewable in app, downloadable.

---

## Data Models

### Feedback Item
```json
{
  "id": "fb_001",
  "org_id": "org_acme",
  "text": "Your checkout flow is confusing. I got stuck at the payment step twice.",
  "source": "app_store_review",
  "sentiment": "negative",
  "sentiment_score": -0.72,
  "rating": 2,
  "customer_id": "cust_042",
  "customer_segment": "enterprise",
  "product_area": "checkout",
  "tags": ["payment", "confusion"],
  "created_at": "2026-02-10T14:30:00Z",
  "ingested_at": "2026-02-10T14:31:00Z",
  "ingestion_method": "csv_upload"
}
```

### Customer Profile
```json
{
  "customer_id": "cust_042",
  "org_id": "org_acme",
  "company_name": "TechFlow Inc",
  "segment": "enterprise",
  "plan": "Enterprise Pro",
  "mrr": 2500,
  "arr": 30000,
  "account_manager": "Sarah Chen",
  "renewal_date": "2026-04-15",
  "health_score": 72,
  "employee_count": 450,
  "industry": "fintech",
  "created_at": "2025-03-10T00:00:00Z"
}
```

### Product Context (from wizard)
```json
{
  "org_id": "org_acme",
  "type": "product_area",
  "name": "Checkout Flow",
  "product_area": "checkout",
  "team": "Payments Team",
  "team_lead": "Mike Rodriguez",
  "description": "Multi-step purchase and payment flow"
}
```

---

## Tech Stack

### Backend
- Python 3.11+ with FastAPI
- Elasticsearch 8.x (Elastic Cloud) — ONLY datastore
- ELSER for semantic search
- ES|QL for analytics
- Agent Builder for conversational agent
- Pydantic for validation
- JWT for auth (python-jose + passlib)

### Frontend
- React 18+ with TypeScript
- Vite build tool
- Tailwind CSS (dark mode via class strategy)
- Axios for API calls
- Lucide React for icons
- React Router for navigation

### Infrastructure
- Docker Compose for local dev (backend + frontend)
- Elastic Cloud for ES + Kibana
- MIT License

---

## Build Phases

| Phase | What | Key Deliverable |
|-------|------|----------------|
| 1 | Foundation + Auth + ES | docker compose up → login → empty dashboard |
| 2 | Product Setup Wizard | 8-step wizard, product context in ES |
| 3 | Data Ingestion | CSV upload, manual entry, feedback + customer data in ES |
| 4 | Search + Feedback Page | Semantic search, filters, feedback detail slide-out |
| 5 | Agent + Tools | ES Agent Builder, 7 tools, chat panel in React |
| 6 | Spec Generation | 4-doc output, saved history, spec viewer |
| 7 | Dashboard + Analytics | 9 widgets, Kibana embedded, customers page |
| 8 | Polish + Ship | Settings, responsive, README, demo video |

Detailed specs for each phase in docs/PHASE_X_SPEC.md.

---

## Current Status
- [x] Architecture designed (8 layers)
- [x] UX mapped (every screen, every interaction — see UX.md)
- [x] Cursor rules configured
- [x] PROJECT.md written
- [x] UX.md written
- [x] TASKS.md written
- [x] Phase 1 spec written
- [ ] Phase 1: Foundation + Auth + ES
- [ ] Phase 2: Product Setup Wizard
- [ ] Phase 3: Data Ingestion
- [ ] Phase 4: Search + Feedback Page
- [ ] Phase 5: Agent + Tools
- [ ] Phase 6: Spec Generation
- [ ] Phase 7: Dashboard + Analytics
- [ ] Phase 8: Polish + Ship
