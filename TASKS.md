# TASKS.md — Context Engine v2 Implementation Plan

> **Full product build. Team of 4 with Cursor + Claude.**
> Each phase has a detailed spec in docs/PHASE_X_SPEC.md.
> Give each spec to Cursor → Cursor plans → you approve → Cursor builds.

---

## Workflow

1. **Read the phase spec** (docs/PHASE_X_SPEC.md)
2. **Give it to Cursor:** "Read docs/PHASE_X_SPEC.md, PROJECT.md, and UX.md. Create a plan. Wait for approval."
3. **Review Cursor's plan** — push back if it deviates from spec
4. **Approve → Cursor builds**
5. **Run acceptance criteria** at the end of each phase
6. **Come back for next phase spec**

---

## Phase Overview

| Phase | What | Depends On | Key Deliverable |
|-------|------|-----------|----------------|
| 1 | Foundation + Auth + ES | Nothing | docker compose up → login → empty dashboard |
| 2 | Product Setup Wizard | Phase 1 | 8-step wizard, product context in ES, onboarding flow |
| 3 | Data Ingestion | Phase 1 | CSV upload, manual entry, feedback + customers in ES |
| 4 | Search + Feedback Page | Phase 3 | Semantic search, filters, detail slide-out, customer page |
| 5 | Agent + Tools | Phase 3, 4 | Agent Builder, 7 tools, chat panel working |
| 6 | Spec Generation | Phase 5 | 4-doc output, saved history, spec viewer |
| 7 | Dashboard + Analytics | Phase 3, 4 | 9 dashboard widgets, Kibana embedded, charts |
| 8 | Polish + Ship | All | Settings complete, responsive, README, demo |

Note: Phases 2 and 3 can run in parallel (different people). Phases 4-7 have dependencies.

---

## Phase 1: Foundation + Auth + ES
**Spec:** docs/PHASE_1_SPEC.md ✅ (written)
**Status:** [ ] Not started

### What gets built
- Docker Compose (backend + frontend)
- FastAPI backend with health check
- Elasticsearch connection (Elastic Cloud)
- users + organizations indexes auto-created
- JWT auth (signup, login, /me)
- React frontend shell: login, signup, sidebar, empty pages, dark theme, agent bubble
- Settings > Elasticsearch shows connection status

### Acceptance criteria (24 items)
See PHASE_1_SPEC.md for full list.

### Key files created
```
docker-compose.yml, .env.example, .gitignore
backend/: Dockerfile, requirements.txt, app/main.py, config.py, es_client.py,
          dependencies.py, models/user.py, schemas/auth.py, schemas/common.py,
          routers/auth.py, routers/health.py, services/auth_service.py,
          services/es_service.py, utils/security.py
frontend/: Dockerfile, package.json, vite.config.ts, tailwind.config.js,
           src/App.tsx, components/layout/Sidebar.tsx, AppLayout.tsx,
           ThemeToggle.tsx, agent/AgentChatBubble.tsx, pages/*.tsx,
           hooks/useAuth.ts, useTheme.ts, services/api.ts
```

---

## Phase 2: Product Setup Wizard
**Spec:** docs/PHASE_2_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- 8-step product wizard UI (React)
- Product context stored in ES ({org_id}-product-context index)
- Onboarding flow for first-time users
- Settings > Product Wizard page (same wizard, editable)
- Agent system prompt auto-populated from product context
- Auto-detect product areas (used later in Phase 3 after feedback upload)

### Wizard steps
1. Product basics (name, description, industry, stage)
2. Product areas / modules
3. Business goals / OKRs
4. Customer segments + pricing tiers
5. Competitors
6. Roadmap (existing + planned features)
7. Team structure
8. Tech stack

### Key endpoints
- POST /api/v1/product/wizard — save wizard step data
- GET /api/v1/product/wizard — get all wizard data for org
- PUT /api/v1/product/wizard/{step} — update specific step
- GET /api/v1/product/context — full product context (for agent system prompt)

---

## Phase 3: Data Ingestion
**Spec:** docs/PHASE_3_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- Feedback CSV upload with column mapping + preview
- Feedback manual entry form
- Customer CSV upload with column mapping
- Customer manual entry form
- {org_id}-feedback index with ELSER semantic_text field
- {org_id}-customers index
- Auto-detect product areas from uploaded feedback text
- Sentiment analysis on ingest
- Bulk ingestion via ES Bulk API
- Upload history in Settings > Data Upload

### Key endpoints
- POST /api/v1/feedback/upload-csv — CSV upload with column mapping
- POST /api/v1/feedback/manual — single feedback entry
- GET /api/v1/feedback — list feedback (paginated, filtered)
- GET /api/v1/feedback/{id} — single feedback item
- POST /api/v1/customers/upload-csv — customer CSV upload
- POST /api/v1/customers/manual — single customer entry
- GET /api/v1/customers — list customers
- GET /api/v1/customers/{id} — single customer profile

### 11 feedback source types
app_store_review, g2_capterra, support_ticket, nps_csat_survey, customer_email, sales_call_note, slack_message, internal_team, user_interview, bug_report, community_forum

---

## Phase 4: Search + Feedback Page + Customer Page
**Spec:** docs/PHASE_4_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- Semantic search (ELSER hybrid: keyword + vector)
- Feedback page: search bar, filters, results list, slide-out detail panel
- Feedback detail: full text, customer card, similar feedback (vector similarity)
- Customer page: list with filters, full profile with metrics, sentiment trend, feedback history
- Filter state in URL (shareable)
- "Ask agent about this" and "Generate spec" action buttons (wire to chat in Phase 5)

### Key endpoints
- POST /api/v1/search/feedback — hybrid semantic + keyword search with filters
- GET /api/v1/feedback/{id}/similar — vector similarity search
- GET /api/v1/customers/{id}/feedback — all feedback for a customer
- GET /api/v1/customers/{id}/sentiment-trend — sentiment over time

---

## Phase 5: Agent + Tools
**Spec:** docs/PHASE_5_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- Elasticsearch Agent Builder configuration
- 7 agent tools:
  1. search_feedback — hybrid search + filters
  2. trend_analysis — time period comparison via ES|QL
  3. top_issues — ranked by impact × growth × revenue
  4. find_similar — vector clustering
  5. customer_lookup — profile + feedback history
  6. compare_segments — enterprise vs SMB vs trial
  7. generate_spec — produces 4 docs (wired in Phase 6)
- Agent system prompt with full product context injected
- Agent chat API endpoint (proxy to Agent Builder)
- React agent chat panel (functional — replaces Phase 1 placeholder)
- Context-aware pre-fills from dashboard, feedback, customer pages
- Conversation history within session

### Key endpoints
- POST /api/v1/agent/chat — send message, get agent response
- GET /api/v1/agent/conversations — past conversations
- GET /api/v1/agent/conversations/{id} — single conversation

---

## Phase 6: Spec Generation
**Spec:** docs/PHASE_6_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- generate_spec agent tool (full implementation)
- 4 spec templates: PRD, Architecture, Rules, Plan
- Specs stored in {org_id}-specs index
- Specs page: list of saved specs, status badges
- Spec detail page: 4-tab viewer, markdown rendering
- Highlighted feedback quotes (clickable to source)
- Customer names + ARR cited (clickable to profile)
- Competitor references from product context
- Team assignments from product context
- Actions: download (markdown/PDF), copy, share link, regenerate, edit, status change

### Key endpoints
- POST /api/v1/specs/generate — trigger spec generation for topic
- GET /api/v1/specs — list saved specs
- GET /api/v1/specs/{id} — single spec (all 4 docs)
- PUT /api/v1/specs/{id} — update spec (edit, status change)
- DELETE /api/v1/specs/{id} — delete spec

---

## Phase 7: Dashboard + Analytics
**Spec:** docs/PHASE_7_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- Dashboard page with 9 widgets (all functional):
  1. Summary cards (total, sentiment, issues, at-risk)
  2. Feedback volume over time (line chart)
  3. Sentiment breakdown (donut)
  4. Top issues (ranked cards with investigate/generate buttons)
  5. Product area breakdown (bar chart)
  6. At-risk customers (table)
  7. Recent feedback stream
  8. Source distribution (pie)
  9. Feedback by segment (stacked bar)
- "Customize Dashboard" — show/hide widgets, saved per user
- Date range selector affecting all widgets
- Kibana dashboards configured (3 pre-built)
- Analytics page: Kibana embedded via iframe (overview, trends, deep dive tabs)
- "Open in Kibana" links
- Dashboard widgets link to Feedback/Customer pages with pre-applied filters

### Key endpoints
- GET /api/v1/analytics/summary — card metrics
- GET /api/v1/analytics/volume — feedback over time
- GET /api/v1/analytics/sentiment — breakdown
- GET /api/v1/analytics/top-issues — ranked issues
- GET /api/v1/analytics/areas — product area stats
- GET /api/v1/analytics/at-risk — at-risk customers
- GET /api/v1/analytics/sources — source distribution
- GET /api/v1/analytics/segments — segment comparison
- GET /api/v1/user/preferences — dashboard widget preferences
- PUT /api/v1/user/preferences — save widget preferences

---

## Phase 8: Polish + Ship
**Spec:** docs/PHASE_8_SPEC.md (not yet written)
**Status:** [ ] Not started

### What gets built
- Settings page complete: all tabs functional
- Settings > Connectors: Slack integration (OAuth, channel selection)
- Settings > Account: email, password change, theme, org name
- Settings > Elasticsearch: connection, index stats, re-index, clear data
- Responsive behavior (sidebar collapse, tablet, mobile basics)
- Empty states polished on all pages
- Loading states on all data fetches
- Error handling on all API calls
- README.md (setup guide, screenshots, architecture, tech stack)
- Demo video script (docs/demo_script.md)
- MIT License
- .gitignore verified
- Final testing: fresh clone → docker compose up → full workflow

---

## Current Status

**You are here → Phase 1**

### Done
- [x] Architecture designed (8 layers)
- [x] UX mapped (UX.md — every screen)
- [x] Cursor rules configured
- [x] PROJECT.md written
- [x] UX.md written
- [x] TASKS.md written
- [x] Phase 1 spec written (docs/PHASE_1_SPEC.md)

### Next
- [ ] Give Phase 1 spec to Cursor
- [ ] Review Cursor's plan
- [ ] Approve → Cursor builds Phase 1
- [ ] Run Phase 1 acceptance criteria
- [ ] Come back for Phase 2 spec
