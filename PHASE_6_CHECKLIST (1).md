# Phase 6 Checklist — Spec Generation

> Walk through EVERY item below after Cursor finishes Phase 6.
> You need: feedback + customer data (Phase 3), working agent (Phase 5), product wizard filled (Phase 2).
> This is the crown jewel — feedback intelligence turned into actionable engineering documents.

---

## Pre-Check: Phases 1-5 Still Work

- [ ] `docker compose up` starts without errors
- [ ] Log in → dashboard
- [ ] Feedback search works (semantic)
- [ ] Customer profiles work
- [ ] Agent chat works — send a message, get response with tool usage
- [ ] Product wizard data still intact in Settings
- [ ] ANTHROPIC_API_KEY valid in .env

---

## A. Generate Specs via Agent Chat

### A1. Trigger Generation
- [ ] Open agent chat
- [ ] Type: "Generate specs for checkout issues"
- [ ] Agent responds: data gathering phase first
  - [ ] "Searching feedback about checkout..." (tool indicator)
  - [ ] "Found X feedback items from Y customers ($Z ARR)"
- [ ] Agent then generates specs:
  - [ ] "Generating 4 spec documents..." (loading indicator)
  - [ ] Generation takes 15-60 seconds (4 Claude API calls)
- [ ] Agent shows completion summary:
  - [ ] Spec title (e.g., "Checkout Issues" or more specific)
  - [ ] Feedback count analyzed
  - [ ] Customers cited + ARR
  - [ ] Status: Draft

### A2. View Full Specs Link
- [ ] Agent response includes [View Full Specs] button/link
- [ ] Click → navigates to /specs/{new_id}
- [ ] Spec detail page loads with all 4 documents

### A3. Generate Another
- [ ] Go back to chat
- [ ] Type: "Generate specs for dashboard performance problems"
- [ ] Second spec generated successfully
- [ ] Navigate to Specs list → both specs visible

---

## B. Specs List Page

### B1. List Display
- [ ] Go to Specs page (sidebar)
- [ ] See generated spec(s) as cards
- [ ] Each card shows:
  - [ ] Title (large text)
  - [ ] Product area tag
  - [ ] Date generated (relative: "5 minutes ago")
  - [ ] Feedback count + customer count
  - [ ] Status badge: "Draft" (gray)
  - [ ] First paragraph of PRD as preview text
- [ ] Click card → navigates to /specs/{id}

### B2. Generate New Spec Button
- [ ] "Generate New Spec" button visible at top
- [ ] Click → opens agent chat (with or without pre-filled prompt)

### B3. Filters
- [ ] Product area filter → filters specs by area
- [ ] Status filter → Draft / Final / Shared
- [ ] Date range filter works

### B4. Sort
- [ ] Default: newest first
- [ ] Specs sorted correctly by date

### B5. Empty State
- [ ] Log in as new user with no specs
- [ ] Specs page shows: "No specs yet. Ask the agent to create your first spec."
- [ ] CTA: [Open Agent Chat]

---

## C. Spec Detail Page — 4-Tab Viewer

### C1. Navigation
- [ ] Click spec from list → URL changes to /specs/{id}
- [ ] Page loads with spec title, metadata, and tab viewer
- [ ] Browser back → returns to specs list

### C2. Tab Navigation
- [ ] 4 tabs visible: [ PRD ] [ Architecture ] [ Rules ] [ Plan ]
- [ ] PRD tab active by default
- [ ] Click "Architecture" → content switches
- [ ] Click "Rules" → content switches
- [ ] Click "Plan" → content switches
- [ ] Click "PRD" → back to PRD
- [ ] Active tab visually highlighted
- [ ] Tab switch is instant (all content loaded, not re-fetched per tab)

### C3. PRD Content
- [ ] Full markdown rendered with styling
- [ ] Has sections: Problem Statement, User Stories, Requirements, Success Metrics, Out of Scope, Open Questions
- [ ] **Feedback citations present:** actual quotes from your feedback data
  - [ ] Quotes visually highlighted (different background or border)
  - [ ] Click a citation → navigates to feedback item (or opens detail)
- [ ] **Customer names present:** real customer names from your data
  - [ ] Customer names clickable → /customers/{id}
  - [ ] ARR mentioned alongside customer names
- [ ] **Business goals referenced:** mentions goals from your wizard
- [ ] **Competitor mentions:** references competitors from wizard
- [ ] **Team assignment:** mentions recommended team from wizard
- [ ] Requirements have priority labels (P0, P1, P2, P3)

### C4. Architecture Content
- [ ] Click Architecture tab
- [ ] Has sections: System Overview, Technical Approach, Data Model, API Changes, Dependencies, Migration, Performance, Security
- [ ] References your tech stack from wizard (e.g., "Current frontend is React 18...")
- [ ] References existing features from roadmap
- [ ] Technical content is specific (not generic boilerplate)

### C5. Rules Content
- [ ] Click Rules tab
- [ ] Has sections: Coding Standards, Error Handling, Testing, Logging, Rollback, Edge Cases, Accessibility, Documentation
- [ ] Edge cases section cites real feedback ("One customer reported...")
- [ ] Testing section has specific test cases derived from feedback

### C6. Plan Content
- [ ] Click Plan tab
- [ ] Has sections: Phase Breakdown, Task List, Dependencies, Team Assignments, Timeline, Risks, Definition of Done, Launch Checklist
- [ ] Team assignments use real team names from wizard
- [ ] Timeline has time estimates
- [ ] Tasks are specific to the issue (not generic)

### C7. Markdown Rendering Quality
- [ ] Headings (H1, H2, H3) render with proper hierarchy
- [ ] Bold text renders bold
- [ ] Lists (bullet + numbered) render correctly
- [ ] Tables render as tables (if present)
- [ ] Code blocks render with styling (if present)
- [ ] All renders correctly in dark mode
- [ ] All renders correctly in light mode
- [ ] Long documents are scrollable

---

## D. Sidebar Metadata

- [ ] Right sidebar (or top area) shows metadata:
  - [ ] Generated by: your user name
  - [ ] Date generated: correct timestamp
  - [ ] Feedback items analyzed: count (matches what agent reported)
  - [ ] Customers cited: count
  - [ ] Product area: correct area
  - [ ] Data freshness: "Based on feedback through [date]"
  - [ ] Linked business goal: shown if relevant (from wizard)

---

## E. Citations — Clickable Links

### E1. Feedback Citations
- [ ] Find a feedback quote in the PRD (highlighted block)
- [ ] Click it → navigates to feedback detail or /feedback?id={id}
- [ ] Feedback detail shows the full item matching the quote
- [ ] Browser back → returns to spec

### E2. Customer Citations
- [ ] Find a customer name in the PRD (bold or linked)
- [ ] Click it → navigates to /customers/{id}
- [ ] Customer profile page loads for that customer
- [ ] Browser back → returns to spec

### E3. Broken Citations
- [ ] If a cited feedback item was deleted → link should handle gracefully (not crash, show "not found")

---

## F. Actions

### F1. Download All
- [ ] Click "Download All" button
- [ ] Downloads a zip file (or 4 separate markdown files)
- [ ] Zip contains: prd.md, architecture.md, rules.md, plan.md
- [ ] Open each file → content matches what's shown in the app
- [ ] Files are valid markdown

### F2. Download Current Tab
- [ ] On PRD tab → click "Download [PRD]"
- [ ] Downloads single prd.md file
- [ ] Switch to Architecture tab → download → architecture.md
- [ ] Content matches displayed content

### F3. Copy to Clipboard
- [ ] On PRD tab → click "Copy to Clipboard"
- [ ] Paste in text editor → full PRD markdown pasted
- [ ] Switch to Architecture → copy → correct content
- [ ] Success toast/notification after copy

### F4. Status Change
- [ ] Default status: Draft (gray badge)
- [ ] Click status dropdown → see options: Draft, Final, Shared
- [ ] Change to "Final" → badge turns green
- [ ] Refresh page → still "Final"
- [ ] Change to "Shared" → badge turns blue
- [ ] Change back to "Draft" → badge turns gray

### F5. Edit Mode
- [ ] With status "Draft": click "Edit" button
- [ ] Markdown viewer switches to textarea/editor
- [ ] Can modify the PRD content
- [ ] Click "Save" → changes saved
- [ ] View mode shows updated content
- [ ] Refresh → edits persisted

### F6. Edit Restrictions
- [ ] Change status to "Final"
- [ ] "Edit" button should be disabled or hidden
- [ ] Cannot edit Final or Shared specs (only Draft)

### F7. Regenerate
- [ ] Click "Regenerate" button
- [ ] Loading state shown (15-60 seconds)
- [ ] New content generated for all 4 docs
- [ ] Spec ID stays the same (URL doesn't change)
- [ ] Updated content is different from original (re-generated, not cached)
- [ ] "Updated at" timestamp changes
- [ ] Previous edits are overwritten (regeneration replaces everything)

### F8. Delete
- [ ] Go to specs list → or spec detail page
- [ ] Click "Delete" → confirmation dialog
- [ ] Confirm → spec removed
- [ ] Redirected to specs list
- [ ] Deleted spec no longer in list
- [ ] Going to /specs/{deleted_id} directly → 404 or "Spec not found"

---

## G. Agent Integration (End-to-End)

### G1. Full Flow
- [ ] Open agent chat
- [ ] Type: "Generate specs for [a real issue in your data]"
- [ ] Agent gathers data → shows summary → generates specs
- [ ] Click [View Full Specs] → spec detail page
- [ ] All 4 tabs have real content
- [ ] Citations link to real feedback/customers
- [ ] Download all 4 files
- [ ] Change status to Final
- [ ] Go to specs list → spec shows with Final badge

### G2. Generate from Feedback Page
- [ ] Go to Feedback → open detail slide-out
- [ ] Click "Generate spec" button
- [ ] Agent chat opens with pre-filled: "Generate specs for [topic]"
- [ ] Agent generates → specs saved

### G3. Multiple Specs
- [ ] Generate 3+ specs on different topics
- [ ] Specs list shows all of them
- [ ] Each has correct title, area, counts
- [ ] Filter by product area → correct specs shown
- [ ] Filter by status → correct specs shown

---

## H. Spec Content Quality

### H1. PRD Quality
- [ ] Problem statement is specific to your data (not generic)
- [ ] User stories reference real feedback patterns
- [ ] Requirements trace to actual feedback items
- [ ] Success metrics are measurable
- [ ] Out of scope section makes sense
- [ ] Document length: 500-2000 words (substantial, not stub)

### H2. Architecture Quality
- [ ] References your actual tech stack
- [ ] Technical approach is relevant to the issue
- [ ] Not a copy of PRD — has technical depth

### H3. Rules Quality
- [ ] Edge cases derived from real feedback
- [ ] Testing requirements are specific
- [ ] Not generic boilerplate

### H4. Plan Quality
- [ ] Tasks are specific, not vague
- [ ] Team assignments match wizard data
- [ ] Timeline is realistic (not "1 day" for complex work)
- [ ] Phases make logical sense

### H5. Cross-Document Consistency
- [ ] All 4 docs reference the same issue/topic
- [ ] Requirements in PRD align with tasks in Plan
- [ ] Architecture aligns with tech stack in Rules
- [ ] No contradictions between documents

---

## I. API Verification (curl or devtools)

### I1. Generate
- [ ] `POST /api/v1/specs/generate` with `{"topic": "test", "product_area": "checkout"}` → 200
- [ ] Response has: id, title, status "draft", feedback_count, customer_count, total_arr

### I2. List
- [ ] `GET /api/v1/specs` → 200, paginated list
- [ ] Each item has: id, title, product_area, status, feedback_count, created_at

### I3. Get Single
- [ ] `GET /api/v1/specs/{id}` → 200, full spec
- [ ] Response has: prd, architecture, rules, plan (all non-empty strings)
- [ ] Response has: feedback_ids array, customer_ids array, data_brief object

### I4. Update
- [ ] `PUT /api/v1/specs/{id}` with `{"status": "final"}` → 200, status updated
- [ ] `PUT /api/v1/specs/{id}` with `{"prd": "# Updated"}` → 200, content updated

### I5. Delete
- [ ] `DELETE /api/v1/specs/{id}` → 200
- [ ] `GET /api/v1/specs/{id}` → 404

### I6. Regenerate
- [ ] `POST /api/v1/specs/{id}/regenerate` → 200, new content
- [ ] prd/architecture/rules/plan content changed from original

### I7. Auth + Multi-Tenant
- [ ] Without JWT → 401
- [ ] Org A specs not visible to Org B

---

## J. Elasticsearch Verification

- [ ] Open Kibana → check `{org_id}-specs` index exists
- [ ] `GET {org_id}-specs/_search` → see stored specs
- [ ] Each spec document has: id, org_id, title, topic, status, prd, architecture, rules, plan
- [ ] prd/architecture/rules/plan are non-empty text fields
- [ ] feedback_ids is an array of valid feedback IDs
- [ ] customer_ids is an array of valid customer IDs
- [ ] data_brief is a stored object (for regeneration)

---

## K. Edge Cases

- [ ] Generate spec on topic with very few feedback items (1-2) → generates (may be shorter), no crash
- [ ] Generate spec on topic with 0 matching feedback → agent says "Not enough data" or generates minimal spec
- [ ] Generate spec with no product wizard data → generates without product context references (no crash)
- [ ] Regenerate a "Final" status spec → should it be allowed? (Check: either blocked or resets to Draft)
- [ ] Very long spec content → page renders without breaking layout
- [ ] Edit spec, add invalid markdown → renders whatever it can, doesn't crash
- [ ] Two users generate specs simultaneously → both succeed, no conflicts
- [ ] Spec title with special characters → saves and displays correctly

---

## L. UI/UX Quality

- [ ] Spec list cards visually clean in dark mode
- [ ] Spec detail page: 4-tab navigation clear and clickable
- [ ] Active tab visually distinct
- [ ] Markdown rendering beautiful in dark mode (headings, code blocks, tables)
- [ ] Markdown rendering works in light mode
- [ ] Citation highlight blocks visible and attractive
- [ ] Status badges: Draft (gray), Final (green), Shared (blue) — colors distinct
- [ ] Loading state during generation (15-60 sec is a LONG wait — needs clear feedback)
- [ ] Download buttons clearly labeled
- [ ] Edit mode toggle obvious
- [ ] Sidebar metadata readable and well-organized
- [ ] Agent chat bubble still visible on spec pages
- [ ] No layout shift when switching tabs

---

## M. Backend Tests

- [ ] Run: `docker compose exec backend pytest`
- [ ] All Phase 1-5 tests still pass
- [ ] All Phase 6 tests pass:
  - [ ] test_spec_service.py (9 tests)
  - [ ] test_spec_routes.py (8 tests)
- [ ] No test failures

---

## N. Frontend Build

- [ ] No TypeScript errors: `docker compose exec frontend npx tsc --noEmit`
- [ ] No console errors during spec generation and viewing
- [ ] No React warnings

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| Pre-Check (Phases 1-5) | 7 | [ ] |
| A. Generate via Agent | 12 | [ ] |
| B. Specs List Page | 10 | [ ] |
| C. 4-Tab Viewer | 25 | [ ] |
| D. Sidebar Metadata | 7 | [ ] |
| E. Citations (clickable) | 5 | [ ] |
| F. Actions | 22 | [ ] |
| G. Agent Integration E2E | 9 | [ ] |
| H. Spec Content Quality | 16 | [ ] |
| I. API Verification | 10 | [ ] |
| J. ES Verification | 6 | [ ] |
| K. Edge Cases | 8 | [ ] |
| L. UI/UX Quality | 13 | [ ] |
| M. Backend Tests | 4 | [ ] |
| N. Frontend Build | 3 | [ ] |
| **TOTAL** | **~157** | |

**Phase 6 is DONE when every box above is checked.**
