# Phase 2: Product Setup Wizard + Onboarding

> **Goal:** First-time PMs go through an optional 8-step wizard to tell the system about their product. This context powers the agent in later phases — it will know your product areas, goals, competitors, roadmap, teams, and tech stack. Returning PMs can edit everything in Settings > Product Wizard.
>
> **Done means:** A new PM signs up and sees the onboarding flow. They can go through 8 wizard steps (all skippable). Data saves to Elasticsearch. They can revisit and edit in Settings. The product context endpoint returns all wizard data for future agent injection.

---

## Context for the AI Agent

This is Phase 2 of 8. Phase 1 is complete — you have a working FastAPI backend, React frontend, JWT auth, Elasticsearch connection, sidebar, empty pages, and agent chat bubble.

In this phase you are building the product context layer. This is how the PM tells the system about their product. Every future phase uses this data: the agent references it in specs, search uses product areas for filtering, dashboard shows product area breakdowns.

Read `.cursorrules` before starting. Read `UX.md` Flow 2 (Onboarding) and Flow 8 (Settings > Product Wizard) for exact UI details.

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Onboarding flow | Welcome screen + 3-section progress (Product → Feedback → Customers). Only Product section built in this phase. |
| Product Wizard (8 steps) | Multi-step form that collects product context. Same UI in onboarding and Settings. |
| Product Context API | CRUD endpoints for all 8 wizard sections. |
| ES Index | `{org_id}-product-context` index storing all wizard data. |
| Settings > Product Wizard | Same wizard, pre-filled with saved data, editable anytime. |
| Product Context endpoint | Single endpoint returning ALL product context — used by agent in Phase 5. |

---

## Database: Elasticsearch Index

### Index: `{org_id}-product-context`

Created when PM first saves any wizard step. One document per wizard section (8 max per org).

**Document structure (each section is one document):**

| Field | ES Type | Purpose |
|-------|---------|---------|
| id | keyword | Auto-generated UUID |
| org_id | keyword | Multi-tenancy |
| section | keyword | One of: basics, areas, goals, segments, competitors, roadmap, teams, tech_stack |
| data | object (dynamic) | Section-specific data (see below) |
| updated_at | date | Last modified |
| created_at | date | First created |

**Section: basics**
```json
{
  "section": "basics",
  "data": {
    "product_name": "Acme Analytics",
    "description": "B2B SaaS data analytics platform",
    "industry": "SaaS",
    "stage": "Growth",
    "website_url": "https://acme-analytics.com"
  }
}
```

**Section: areas**
```json
{
  "section": "areas",
  "data": {
    "areas": [
      { "id": "area_001", "name": "Checkout Flow", "description": "Multi-step purchase and payment flow", "order": 0 },
      { "id": "area_002", "name": "Dashboard", "description": "Main analytics dashboard", "order": 1 }
    ]
  }
}
```

**Section: goals**
```json
{
  "section": "goals",
  "data": {
    "goals": [
      {
        "id": "goal_001",
        "time_period": "Q1 2026",
        "title": "Reduce checkout abandonment by 30%",
        "description": "Checkout drop-off is our #1 growth bottleneck",
        "priority": "P0",
        "linked_area_id": "area_001"
      }
    ]
  }
}
```

**Section: segments**
```json
{
  "section": "segments",
  "data": {
    "segments": [
      { "id": "seg_001", "name": "Enterprise", "description": "500+ employees", "revenue_share": 60 },
      { "id": "seg_002", "name": "SMB", "description": "50-500 employees", "revenue_share": 30 }
    ],
    "pricing_tiers": [
      { "id": "tier_001", "name": "Enterprise Pro", "price": 2500, "price_period": "month", "segment_id": "seg_001", "features": "Unlimited users, SSO, dedicated support" }
    ]
  }
}
```

**Section: competitors**
```json
{
  "section": "competitors",
  "data": {
    "competitors": [
      {
        "id": "comp_001",
        "name": "Mixpanel",
        "website": "https://mixpanel.com",
        "strengths": "Great funnel analytics, fast UI",
        "weaknesses": "No feedback integration, expensive at scale",
        "differentiation": "We combine analytics with customer voice"
      }
    ]
  }
}
```

**Section: roadmap**
```json
{
  "section": "roadmap",
  "data": {
    "existing_features": [
      { "id": "feat_001", "name": "Basic Dashboard", "area_id": "area_002", "status": "live", "release_date": "2025-01" }
    ],
    "planned_features": [
      { "id": "feat_002", "name": "Advanced Filtering", "area_id": "area_002", "status": "planned", "target_date": "Q2 2026", "priority": "P1" }
    ]
  }
}
```

**Section: teams**
```json
{
  "section": "teams",
  "data": {
    "teams": [
      {
        "id": "team_001",
        "name": "Payments Team",
        "lead": "Mike Rodriguez",
        "area_ids": ["area_001"],
        "size": 6,
        "slack_channel": "#team-payments"
      }
    ]
  }
}
```

**Section: tech_stack**
```json
{
  "section": "tech_stack",
  "data": {
    "technologies": [
      { "id": "tech_001", "category": "Frontend", "technology": "React 18", "notes": "With Next.js, deployed on Vercel" },
      { "id": "tech_002", "category": "Backend", "technology": "Node.js", "notes": "Express API" }
    ]
  }
}
```

---

## API Endpoints

All endpoints prefixed with `/api/v1/`. All require JWT auth.

| Method | Path | Description |
|--------|------|-------------|
| PUT | /product/wizard/{section} | Save/update one wizard section |
| GET | /product/wizard | Get all wizard sections for current org |
| GET | /product/wizard/{section} | Get one wizard section |
| DELETE | /product/wizard/{section} | Clear one wizard section |
| GET | /product/context | Get full product context (flattened, for agent prompt) |
| GET | /product/onboarding-status | Check if PM has completed onboarding |
| POST | /product/onboarding-complete | Mark onboarding as complete |

### PUT /product/wizard/{section}

- `section` is one of: basics, areas, goals, segments, competitors, roadmap, teams, tech_stack
- Request body: the `data` object for that section (varies per section — see schemas below)
- Upserts: if section exists, update it. If not, create it.
- Creates `{org_id}-product-context` index if it doesn't exist.
- Returns the saved document.

### GET /product/wizard

- Returns all 8 sections (or however many exist) for current org.
- Response: `{ "data": { "basics": {...}, "areas": {...}, ... }, "completed_sections": ["basics", "areas"] }`

### GET /product/context

- Returns a flattened view of ALL product context. This is what gets injected into the agent's system prompt in Phase 5.
- Combines all sections into one response with product_name, areas list, goals list, etc.
- If no data exists, returns empty structure (not an error).

### GET /product/onboarding-status

- Checks if onboarding_completed flag is set for this org.
- Response: `{ "data": { "completed": false, "completed_sections": ["basics"], "total_sections": 8 } }`
- Store this flag in the organizations index (add field).

### POST /product/onboarding-complete

- Sets onboarding_completed = true on the organization document.
- Response: `{ "data": { "completed": true } }`

---

## Schemas (Pydantic)

### schemas/product.py

**Request schemas (one per section):**

- `ProductBasicsRequest` — product_name (str, required), description (str, optional), industry (str, optional), stage (str, optional), website_url (str, optional)
- `ProductAreaItem` — name (str, required), description (str, optional)
- `ProductAreasRequest` — areas (list[ProductAreaItem])
- `GoalItem` — time_period (str), title (str, required), description (str, optional), priority (str: P0/P1/P2/P3), linked_area_id (str, optional)
- `ProductGoalsRequest` — goals (list[GoalItem])
- `SegmentItem` — name (str), description (str, optional), revenue_share (float, optional)
- `PricingTierItem` — name (str), price (float), price_period (str), segment_id (str, optional), features (str, optional)
- `ProductSegmentsRequest` — segments (list[SegmentItem]), pricing_tiers (list[PricingTierItem], optional)
- `CompetitorItem` — name (str, required), website (str, optional), strengths (str, optional), weaknesses (str, optional), differentiation (str, optional)
- `ProductCompetitorsRequest` — competitors (list[CompetitorItem])
- `ExistingFeatureItem` — name (str), area_id (str, optional), status (str: live/beta/deprecated), release_date (str, optional)
- `PlannedFeatureItem` — name (str), area_id (str, optional), status (str: planned/in_progress/blocked), target_date (str, optional), priority (str, optional)
- `ProductRoadmapRequest` — existing_features (list[ExistingFeatureItem]), planned_features (list[PlannedFeatureItem])
- `TeamItem` — name (str, required), lead (str, optional), area_ids (list[str], optional), size (int, optional), slack_channel (str, optional)
- `ProductTeamsRequest` — teams (list[TeamItem])
- `TechItem` — category (str: Frontend/Backend/Database/Infrastructure/Monitoring/Other), technology (str, required), notes (str, optional)
- `ProductTechStackRequest` — technologies (list[TechItem])

**Response schemas:**
- `WizardSectionResponse` — section (str), data (dict), updated_at (str)
- `WizardAllResponse` — data (dict of section → data), completed_sections (list[str])
- `ProductContextResponse` — flattened: product_name, description, industry, stage, areas (list), goals (list), segments (list), pricing_tiers (list), competitors (list), existing_features (list), planned_features (list), teams (list), technologies (list)
- `OnboardingStatusResponse` — completed (bool), completed_sections (list[str]), total_sections (int)

---

## Services (Backend)

### services/product_service.py

Functions:
- `save_wizard_section(org_id, section, data)` — Upsert section document in `{org_id}-product-context` index.
- `get_wizard_section(org_id, section)` — Get one section. Return None if not found.
- `get_all_wizard_sections(org_id)` — Get all sections for org. Return dict.
- `delete_wizard_section(org_id, section)` — Delete a section document.
- `get_product_context(org_id)` — Build flattened product context from all sections. Returns ProductContextResponse.
- `get_onboarding_status(org_id)` — Check organizations index for onboarding_completed flag + count completed sections.
- `mark_onboarding_complete(org_id)` — Update organization document, set onboarding_completed = true.

### Routers

### routers/product.py

- All endpoints from the API section above.
- All require `current_user: CurrentUser = Depends(get_current_user)`.
- Use `current_user.org_id` for all ES queries.

---

## Frontend

### Onboarding Flow

**OnboardingPage.tsx** (`/onboarding`)

- Shown after first signup (check onboarding-status endpoint on app mount).
- If onboarding not complete → redirect to /onboarding.
- If complete → go to /dashboard.

Welcome screen:
- "Welcome to Context Engine! Let's set up your product."
- Three cards: Product Setup (active) → Upload Feedback (grayed, Phase 3) → Upload Customers (grayed, Phase 3)
- "Skip everything and explore" link → calls onboarding-complete, goes to /dashboard

### Product Wizard Component

**ProductWizard.tsx** (shared between onboarding and settings)

- 8-step flow with progress bar at top
- Each step is a child component:
  - `WizardStepBasics.tsx`
  - `WizardStepAreas.tsx`
  - `WizardStepGoals.tsx`
  - `WizardStepSegments.tsx`
  - `WizardStepCompetitors.tsx`
  - `WizardStepRoadmap.tsx`
  - `WizardStepTeams.tsx`
  - `WizardStepTechStack.tsx`

Each step:
- Loads existing data from API (if editing in Settings)
- Has form fields matching UX.md spec
- "Continue" saves and advances, "Skip" advances without saving, "Back" goes back
- Saves via PUT /product/wizard/{section}
- Shows success feedback (subtle, no page reload)

Step-specific UI details:
- **Areas:** "Add area" button, delete X on each, drag-and-drop reorder, hint text about auto-detection
- **Goals:** "Add goal" button, linked_area dropdown populated from areas step
- **Segments:** Default 4 pre-filled (Enterprise, SMB, Consumer, Trial), editable. Pricing tiers below.
- **Competitors:** "Add competitor" button
- **Roadmap:** Two sections (Existing / Planned), each with "Add feature" button, area dropdowns
- **Teams:** "Add team" button, area_ids multi-select from areas step
- **Tech Stack:** Category dropdown, "Add technology" button

After Step 8 (or after last non-skipped step):
- "Product setup complete!" confirmation
- In onboarding: "Continue to feedback upload" (disabled, Phase 3) or "Go to Dashboard"
- In settings: just saves, no redirect

### Settings Page Updates

**SettingsPage.tsx** — Update the "Product Wizard" tab:
- Render the same ProductWizard component
- Pre-fills all existing data
- No progress bar needed (can use tabs or accordion for each section instead)
- Changes save immediately on "Save" click per section

### Router Updates

Add routes:
- `/onboarding` → OnboardingPage (protected, only if not completed)

### App.tsx Mount Logic

On app mount (after auth check):
1. If not logged in → /login
2. If logged in, check GET /product/onboarding-status
3. If not completed → /onboarding
4. If completed → /dashboard (or requested page)

---

## Organizations Index Update

Add `onboarding_completed` field to the organizations index:

| Field | ES Type | Default |
|-------|---------|---------|
| onboarding_completed | boolean | false |

Update the organization document when PM completes onboarding. This is NOT a new index — update the existing mapping.

---

## Testing

### test_product_service.py
1. Save basics section → verify stored in ES.
2. Save areas section with 3 areas → verify all stored.
3. Get wizard section returns correct data.
4. Get all wizard sections returns only sections that exist.
5. Update existing section → verify updated, not duplicated.
6. Delete section → verify removed.
7. Get product context flattens all sections correctly.
8. Get product context with missing sections returns partial data (no error).
9. Product context only returns data for current org (multi-tenant).

### test_product_routes.py
1. PUT /product/wizard/basics with valid data → 200.
2. PUT /product/wizard/basics with missing product_name → 422.
3. PUT /product/wizard/areas with empty list → 200 (valid, PM cleared areas).
4. GET /product/wizard returns all saved sections.
5. GET /product/wizard/{section} returns that section.
6. GET /product/wizard/{section} for non-existent section → 404.
7. DELETE /product/wizard/{section} → 200.
8. GET /product/context returns flattened data.
9. GET /product/onboarding-status for new user → completed: false.
10. POST /product/onboarding-complete → completed: true.
11. GET /product/onboarding-status after complete → completed: true.
12. All endpoints reject requests without JWT → 401.
13. All endpoints isolate by org_id.

### test_wizard_validation.py
1. Basics: product_name required, others optional.
2. Areas: each area needs a name.
3. Goals: each goal needs a title.
4. Segments: name required on each segment.
5. Competitors: name required on each competitor.
6. Roadmap: feature name required on each item.
7. Teams: team name required.
8. Tech stack: technology name and category required.

---

## Non-Negotiable Rules for This Phase

Everything from Phase 1 still applies, plus:

1. **All wizard steps are optional.** Only product_name in Step 1 is required (and even Step 1 itself is skippable).
2. **Same wizard component in onboarding AND settings.** Don't build two different UIs.
3. **Upsert, not insert.** Saving a section that already exists must update it, not create a duplicate.
4. **Product context endpoint must work with partial data.** If PM only filled 2 of 8 steps, it returns what exists.
5. **org_id isolation.** PM must never see another org's product context.
6. **Each step saves independently.** If PM fills 3 steps and closes browser, those 3 are saved.
7. **IDs on list items.** Every area, goal, segment, etc. gets a UUID. Other sections reference these IDs.

---

## What NOT to Build

- Feedback upload UI or API (Phase 3)
- Customer upload UI or API (Phase 3)
- Auto-detection of product areas from feedback (Phase 3)
- Sentiment analysis (Phase 3)
- Search functionality (Phase 4)
- Agent tools or chat (Phase 5)
- Spec generation (Phase 6)
- Dashboard widgets (Phase 7)
- Slack connector (Phase 8)

---

## Acceptance Criteria

Phase 2 is complete when ALL of these are true:

- [ ] New user after signup is redirected to /onboarding
- [ ] Onboarding welcome screen shows with "Skip everything" option
- [ ] PM can start Product Wizard from onboarding
- [ ] Progress bar shows current step (1 of 8)
- [ ] Step 1 (Basics): PM can enter product name, description, industry, stage, URL
- [ ] Step 2 (Areas): PM can add multiple areas with name + description, reorder them
- [ ] Step 3 (Goals): PM can add goals with period, title, description, priority, linked area
- [ ] Step 4 (Segments): Pre-filled defaults shown, PM can edit/add segments + pricing tiers
- [ ] Step 5 (Competitors): PM can add competitors with all fields
- [ ] Step 6 (Roadmap): PM can add existing and planned features with status/dates
- [ ] Step 7 (Teams): PM can add teams with lead, areas, size, Slack channel
- [ ] Step 8 (Tech Stack): PM can add technologies with category and notes
- [ ] Every step can be skipped without error
- [ ] "Continue" saves data and advances to next step
- [ ] "Back" returns to previous step with data preserved
- [ ] After wizard: "Go to Dashboard" works
- [ ] Returning user goes directly to /dashboard (not onboarding)
- [ ] Settings > Product Wizard shows same wizard with saved data pre-filled
- [ ] PM can edit any section in Settings and save
- [ ] `{org_id}-product-context` index created in ES
- [ ] GET /product/wizard returns all saved sections
- [ ] GET /product/context returns flattened product context
- [ ] All data filtered by org_id (multi-tenant verified by test)
- [ ] All backend tests pass
- [ ] All Phase 1 tests still pass

---

## How to Give This to Cursor

1. Save this file as `docs/PHASE_2_SPEC.md`
2. Open Cursor agent chat:

> Read docs/PHASE_2_SPEC.md, PROJECT.md, and UX.md (Flow 2 and Flow 8). This is the spec for Phase 2. The .cursorrules file applies. Do NOT start building yet. First, create a detailed implementation plan: list every file you will create or modify, what each contains, the order you will work in, and dependencies between files. Present the full plan and wait for my approval before writing any code.

3. Review → Approve → Build → Acceptance criteria.

---

## After Phase 2

Once all acceptance criteria pass, come back for Phase 3: Data Ingestion. That phase will add:
- Feedback CSV upload with column mapping
- Customer CSV upload
- Manual entry forms for both
- ELSER semantic_text field on feedback index
- Auto-detection of product areas from feedback text
- Sentiment analysis on ingest
