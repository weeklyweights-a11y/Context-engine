# Phase 6: Spec Generation

> **Goal:** The agent can generate 4 production-ready engineering spec documents from feedback data. Specs are saved, browsable, editable, downloadable, and cite real feedback + customers.
>
> **Done means:** PM asks "Generate specs for checkout issues". Agent searches feedback, gathers context, produces PRD + Architecture + Rules + Plan. Specs appear on the Specs page. PM can view each tab, see cited feedback/customers, download, edit status, regenerate.

---

## Context for the AI Agent

This is Phase 6 of 8. Phases 1-5 complete — full data pipeline, search, and agent with 7 tools.

This phase is the crown jewel — turning feedback intelligence into actionable engineering documents. The generate_spec tool (prep only in Phase 5) now produces real output.

Read `.cursorrules`. Read `UX.md` Flow 6 (Specs Page) and Flow 9 (Agent spec generation flow).

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Spec generation logic | 4 prompts that produce PRD, Architecture, Rules, Plan from data brief |
| {org_id}-specs index | Store generated specs |
| Specs list page | Browse saved specs with status badges |
| Spec detail page | 4-tab viewer with markdown rendering |
| Feedback citations | Clickable links to source feedback |
| Customer citations | Clickable links to customer profiles |
| Download | Markdown files or PDF |
| Status management | Draft → Final → Shared |
| Regenerate | Re-run generation from spec page |

---

## Spec Generation Flow

### Step 1: Data Gathering (from Phase 5 generate_spec_prep)

Already built. Returns:
- topic, feedback items, affected customers, ARR, sentiment summary
- Related goals, roadmap items, recommended team, competitor context

### Step 2: Generate 4 Documents

For each document, make a separate Claude API call with:
- System prompt: "You are a senior product/engineering writer..."
- Context: all gathered data from Step 1
- Product context: from wizard
- Specific template instructions (see below)

### Document 1: PRD (Product Requirements Document)

Prompt template:
```
Generate a PRD for: {topic}

Based on {feedback_count} customer feedback items affecting {customer_count} customers (${arr_affected} ARR).

## Data Available
{top 10 feedback quotes with customer names and sentiment}

## Product Context
{product areas, goals, segments, competitor info}

## PRD Structure
1. Problem Statement — What's broken, who's affected, business impact
2. User Stories — Derived from real feedback, cite specific customers
3. Requirements — Functional requirements with priority (P0-P3)
4. Success Metrics — Measurable outcomes linked to business goals
5. Out of Scope — What this spec intentionally excludes
6. Open Questions — Unresolved items needing team input

## Rules
- Every requirement must trace to real feedback
- Include exact customer quotes (with attribution)
- Mention specific customer names and ARR when citing impact
- Reference business goals where relevant
- Note competitor approaches where relevant
- Assign to recommended team
- Be specific and actionable, not generic
```

### Document 2: Architecture

```
Generate an Architecture doc for: {topic}

## Structure
1. System Overview — How this fits into existing architecture
2. Technical Approach — Recommended implementation strategy
3. Data Model Changes — New/modified schemas
4. API Changes — New/modified endpoints
5. Dependencies — External services, libraries
6. Migration Strategy — How to roll out safely
7. Performance Considerations — Scale, latency, caching
8. Security Considerations

## Context
Current tech stack: {from wizard}
Existing architecture: {from wizard tech_stack}
Related existing features: {from roadmap}
```

### Document 3: Engineering Rules

```
Generate Engineering Rules for: {topic}

## Structure
1. Coding Standards — Specific to this feature
2. Error Handling — What can go wrong, how to handle
3. Testing Requirements — Unit, integration, e2e test cases
4. Logging & Monitoring — What to log, alerts to set
5. Rollback Plan — How to undo if things break
6. Edge Cases — From real feedback (cite the weird ones)
7. Accessibility Requirements
8. Documentation Requirements
```

### Document 4: Implementation Plan

```
Generate an Implementation Plan for: {topic}

## Structure
1. Phase Breakdown — Split into shippable increments
2. Task List — Specific tasks with time estimates
3. Dependencies — What blocks what
4. Team Assignments — Who does what (use team from product context)
5. Timeline — Realistic schedule
6. Risk Register — What could go wrong
7. Definition of Done — Per phase and overall
8. Launch Checklist — Pre-launch verification steps
```

### Step 3: Save to Elasticsearch

Save all 4 documents as one spec record in `{org_id}-specs` index.

---

## Elasticsearch Index: `{org_id}-specs`

| Field | ES Type | Purpose |
|-------|---------|---------|
| id | keyword | UUID |
| org_id | keyword | Multi-tenancy |
| title | text + keyword | Spec title (from topic) |
| topic | text | Original topic/query |
| product_area | keyword | Primary product area |
| status | keyword | draft / final / shared |
| prd | text | Full PRD markdown |
| architecture | text | Full Architecture markdown |
| rules | text | Full Rules markdown |
| plan | text | Full Plan markdown |
| feedback_count | integer | Items analyzed |
| customer_count | integer | Customers cited |
| total_arr | float | ARR of affected customers |
| feedback_ids | keyword (array) | IDs of cited feedback items |
| customer_ids | keyword (array) | IDs of cited customers |
| linked_goal_id | keyword | Business goal if relevant |
| generated_by | keyword | user_id who triggered |
| data_brief | object | The gathered data from spec_prep (for regeneration) |
| created_at | date | Generated date |
| updated_at | date | Last modified |

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /specs/generate | Yes | Generate specs for a topic |
| GET | /specs | Yes | List saved specs |
| GET | /specs/{id} | Yes | Get full spec (all 4 docs) |
| PUT | /specs/{id} | Yes | Update (edit content, change status) |
| DELETE | /specs/{id} | Yes | Delete spec |
| POST | /specs/{id}/regenerate | Yes | Re-generate from same data |

### POST /api/v1/specs/generate

Request:
```json
{
  "topic": "checkout form state loss",
  "product_area": "checkout"
}
```

Process:
1. Run generate_spec_prep (from Phase 5)
2. Generate 4 documents via Claude API (4 separate calls)
3. Save to {org_id}-specs index
4. Return spec ID + summary

Response:
```json
{
  "data": {
    "id": "spec_001",
    "title": "Checkout Form State Loss",
    "status": "draft",
    "feedback_count": 45,
    "customer_count": 23,
    "total_arr": 450000,
    "created_at": "2026-02-20T14:30:00Z"
  }
}
```

### GET /api/v1/specs/{id}

Returns full spec with all 4 documents:
```json
{
  "data": {
    "id": "spec_001",
    "title": "Checkout Form State Loss",
    "product_area": "checkout",
    "status": "draft",
    "prd": "# PRD: Checkout Form State Loss\n\n## Problem Statement\n...",
    "architecture": "# Architecture: Checkout Form State Loss\n...",
    "rules": "# Engineering Rules\n...",
    "plan": "# Implementation Plan\n...",
    "feedback_count": 45,
    "customer_count": 23,
    "total_arr": 450000,
    "feedback_ids": ["fb_001", "fb_023", ...],
    "customer_ids": ["cust_042", "cust_015", ...],
    "linked_goal_id": "goal_001",
    "generated_by": "user_001",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### PUT /api/v1/specs/{id}

Update status or edit content:
```json
{
  "status": "final",
  "prd": "# Updated PRD content..."
}
```

### POST /api/v1/specs/{id}/regenerate

Re-generates all 4 docs using the saved data_brief. Overwrites existing content. Returns updated spec.

---

## Services (Backend)

### services/spec_service.py
- `generate_specs(org_id, user_id, topic, product_area)` — Full pipeline: prep → generate 4 docs → save
- `generate_prd(data_brief, product_context)` — Claude API call for PRD
- `generate_architecture(data_brief, product_context)` — Claude API call
- `generate_rules(data_brief, product_context)` — Claude API call
- `generate_plan(data_brief, product_context)` — Claude API call
- `save_spec(org_id, spec_data)` — Store in ES
- `get_specs(org_id, page, page_size, filters)` — List specs
- `get_spec(org_id, spec_id)` — Get single spec
- `update_spec(org_id, spec_id, updates)` — Update fields
- `delete_spec(org_id, spec_id)` — Delete
- `regenerate_spec(org_id, spec_id, user_id)` — Re-generate from data_brief

---

## Frontend

### Specs List Page

**SpecsPage.tsx** — Replace empty state.

Cards for each spec:
- Title (large)
- Product area tag
- Date generated (relative)
- Feedback count + customer count
- Status badge: Draft (gray), Final (green), Shared (blue)
- First paragraph of PRD as preview
- Click → /specs/{id}

Top:
- "Generate New Spec" button → opens agent chat with prompt
- Filter: product area, status, date range
- Sort: newest first

### Spec Detail Page

**SpecDetailPage.tsx** — New page at `/specs/{id}`

**4-Tab Navigation:** `[ PRD ] [ Architecture ] [ Rules ] [ Plan ]`

Each tab:
- Renders markdown content with styling (react-markdown or similar)
- Headings, lists, tables, code blocks styled in dark theme
- **Feedback citations:** Quotes wrapped in highlight blocks, clickable → navigates to /feedback?id={feedback_id} or opens detail
- **Customer citations:** Company names in bold, clickable → /customers/{id}
- **Product context references:** Goals, roadmap items highlighted
- **Competitor mentions:** From wizard data
- **Team assignments:** From wizard data

**Sidebar metadata:**
- Generated by: user name
- Date generated
- Feedback items analyzed: count
- Customers cited: count
- Product area
- Data freshness: "Based on feedback through {date}"
- Linked business goal (if any)

**Actions (top-right):**
- "Download All" → zip of 4 markdown files
- "Download [Current Tab]" → single markdown file
- "Copy to Clipboard" → current tab content
- "Regenerate" → POST /specs/{id}/regenerate → loading → refresh
- "Edit" → toggle inline editing (textarea replacing rendered markdown)
- Status dropdown: Draft → Final → Shared

### Agent Integration

Update generate_spec_prep tool → now calls full generate_specs:

Agent flow when PM asks "Generate specs for checkout":
1. Agent: "Let me gather the data..." (calls generate_spec_prep)
2. Agent: "Found 45 feedback items from 23 customers ($450K ARR). Generating specs..."
3. Agent: calls POST /specs/generate behind the scenes
4. Agent: "Done! Generated 4 spec documents for Checkout Form State Loss."
5. Agent shows summary card with: title, feedback count, customers, ARR
6. Agent shows [View Full Specs] button → navigates to /specs/{id}

### Router Updates
- `/specs/:id` → SpecDetailPage (protected)

---

## Testing

### test_spec_service.py
1. Generate specs creates all 4 documents.
2. Generate specs saves to ES with correct fields.
3. Generate specs includes feedback citations.
4. Get specs list returns only current org's specs.
5. Get single spec returns all 4 docs.
6. Update spec status → updated in ES.
7. Update spec content → content updated.
8. Delete spec → removed from ES.
9. Regenerate spec → new content, same ID.

### test_spec_routes.py
1. POST /specs/generate → 200, returns spec ID.
2. GET /specs → paginated list.
3. GET /specs/{id} → full spec with 4 docs.
4. PUT /specs/{id} with status change → updated.
5. DELETE /specs/{id} → 200.
6. POST /specs/{id}/regenerate → new content.
7. All endpoints require auth.
8. All endpoints isolate by org_id.

---

## Non-Negotiable Rules

1. **4 separate documents.** Always PRD + Architecture + Rules + Plan.
2. **Real data citations.** Specs must reference actual feedback quotes and customer names.
3. **Feedback IDs stored.** Every cited feedback item tracked for clickable links.
4. **Data brief saved.** Regeneration uses same data, not a new search.
5. **Status workflow.** Draft → Final → Shared. Only Draft is editable.
6. **org_id isolation.** Multi-tenant on specs.

---

## What NOT to Build

- Dashboard widgets (Phase 7)
- Kibana dashboards (Phase 7)
- Slack connector (Phase 8)
- PDF export (Phase 8 — just markdown download for now)

---

## Acceptance Criteria

- [ ] PM can trigger spec generation from agent chat
- [ ] Agent gathers data and reports summary before generating
- [ ] 4 documents generated (PRD, Architecture, Rules, Plan)
- [ ] Specs saved to {org_id}-specs index
- [ ] Specs list page shows saved specs with status badges
- [ ] Spec detail page shows 4-tab viewer
- [ ] Markdown renders correctly with styling
- [ ] Feedback citations are clickable (link to feedback)
- [ ] Customer citations are clickable (link to customer profile)
- [ ] Product context referenced in specs (goals, competitors, teams)
- [ ] Download markdown files works
- [ ] Copy to clipboard works
- [ ] Status can be changed (Draft → Final → Shared)
- [ ] Edit mode allows inline editing (Draft only)
- [ ] Regenerate creates new content, same spec ID
- [ ] Delete removes spec
- [ ] "View Full Specs" link in agent response works
- [ ] All data filtered by org_id
- [ ] All backend tests pass
- [ ] All previous phase tests still pass

---

## How to Give This to Cursor

> Read docs/PHASE_6_SPEC.md, PROJECT.md, and UX.md (Flow 6, Flow 9 spec generation). This is Phase 6. Create implementation plan, wait for approval.

---

## After Phase 6

Phase 7: Dashboard + Analytics. 9 widgets, Kibana embedded, customers page enhancements.
