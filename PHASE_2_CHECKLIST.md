# Phase 2 Checklist — Product Setup Wizard + Onboarding

> Walk through EVERY item below after Cursor finishes Phase 2.
> Open the app in your browser and test each one manually.
> Check the box only after you've verified it yourself.

**Implementation updates (done):**
- Signup → redirects to /onboarding
- Welcome screen: "Welcome to Context Engine!", 3 sections (Product active, Feedback/Customers grayed), "Skip everything and explore"
- Product Basics: Industry dropdown (SaaS, Fintech, etc.), Stage dropdown (Early stage, Growth, etc.), Continue button
- Product Areas: Add area, Remove (✕), hint text about auto-detection, Continue
- Segments: Pre-filled Enterprise, SMB, Consumer, Trial; revenue share %; pricing tier period, segment, features
- Wizard complete: "Product setup complete!" screen with "Go to Dashboard" and disabled "Continue to feedback upload (Phase 3)"

---

## Pre-Check: Phase 1 Still Works

- [ ] `docker compose up` starts without errors
- [ ] Go to http://localhost:3000 → see login page
- [ ] Log in with existing account → works, goes to dashboard
- [ ] Sidebar shows all 6 nav links
- [ ] Dark mode is default
- [ ] Theme toggle works
- [ ] Agent chat bubble visible bottom-right
- [ ] Settings > Elasticsearch shows "Connected"
- [ ] Log out → redirects to /login

---

## A. Onboarding Flow (New User)

### A1. New Signup → Onboarding Redirect
- [ ] Open incognito / new browser
- [ ] Go to /signup → create a NEW account (different email)
- [ ] After signup → automatically redirected to /onboarding (NOT /dashboard)

### A2. Welcome Screen
- [ ] See "Welcome to Context Engine!" message
- [ ] See three sections: Product → Feedback → Customers
- [ ] Product section is active/clickable
- [ ] Feedback section is grayed out (Phase 3)
- [ ] Customers section is grayed out (Phase 3)
- [ ] "Skip everything and explore" link is visible at bottom

### A3. Skip Everything
- [ ] Click "Skip everything and explore"
- [ ] Redirected to /dashboard
- [ ] Refresh page → stays on /dashboard (not redirected back to onboarding)

---

## B. Product Wizard — Step by Step

> Sign up as ANOTHER new user (or reset onboarding). Go through wizard step by step.

### B1. Step 1: Product Basics
- [ ] Progress bar shows "Step 1 of 8"
- [ ] Product name field is visible (only required field)
- [ ] Description textarea visible
- [ ] Industry dropdown: SaaS, Fintech, Healthcare, E-commerce, Education, Other
- [ ] Stage dropdown: Early stage, Growth, Mature, Enterprise
- [ ] Website URL field visible
- [ ] Type product name: "Test Product"
- [ ] Fill description: "A test product for checklist"
- [ ] Select industry: "SaaS"
- [ ] Select stage: "Growth"
- [ ] Click "Continue"
- [ ] No errors, advances to Step 2

### B2. Step 1: Skip Test
- [ ] Go back, clear product name, try Continue → should show validation error (name required)
- [ ] Click "Skip" instead → advances to Step 2 without error

### B3. Step 2: Product Areas
- [ ] Progress bar shows "Step 2 of 8"
- [ ] Empty state: no areas yet
- [ ] Click "Add area"
- [ ] Type name: "Checkout Flow", description: "Payment and cart"
- [ ] Click "Add area" again
- [ ] Type name: "Dashboard", description: "Analytics views"
- [ ] Click "Add area" again
- [ ] Type name: "User Settings", description: "Account management"
- [ ] See 3 areas listed
- [ ] Delete one area (click X) → removed from list
- [ ] Drag-and-drop reorder works (if implemented) — OR at least order is preserved
- [ ] Hint text about auto-detection is visible
- [ ] Click "Continue"

### B4. Step 3: Business Goals
- [ ] Progress bar shows "Step 3 of 8"
- [ ] Click "Add goal"
- [ ] Time period dropdown: Q1 2026, Q2 2026, H1 2026, etc.
- [ ] Title: "Reduce checkout abandonment by 30%"
- [ ] Description: "Our biggest growth bottleneck"
- [ ] Priority dropdown: P0, P1, P2, P3
- [ ] Linked product area dropdown shows areas from Step 2 (Checkout Flow, Dashboard)
- [ ] Select "Checkout Flow" as linked area
- [ ] Add a second goal
- [ ] Click "Continue"

### B5. Step 4: Customer Segments + Pricing
- [ ] Progress bar shows "Step 4 of 8"
- [ ] Default segments pre-filled: Enterprise, SMB, Consumer, Trial
- [ ] Each segment has: name, description, revenue share %
- [ ] PM can edit default segment names
- [ ] PM can add a new segment
- [ ] PM can delete a segment
- [ ] Revenue shares are editable (number input)
- [ ] Pricing Tiers section below segments
- [ ] Add a pricing tier: name "Enterprise Pro", price 2500, period "month"
- [ ] Segment dropdown on tier shows the segments above
- [ ] Features text field works
- [ ] Click "Continue"

### B6. Step 5: Competitors
- [ ] Progress bar shows "Step 5 of 8"
- [ ] Click "Add competitor"
- [ ] Name: "Mixpanel"
- [ ] Website: "https://mixpanel.com"
- [ ] Strengths: "Great funnel analytics"
- [ ] Weaknesses: "No feedback integration"
- [ ] Differentiation: "We combine analytics with voice"
- [ ] Add a second competitor
- [ ] Click "Continue"

### B7. Step 6: Roadmap
- [ ] Progress bar shows "Step 6 of 8"
- [ ] Two sections: "Existing Features" and "Planned Features"
- [ ] Add existing feature: name "Basic Dashboard", area dropdown shows areas from Step 2
- [ ] Status dropdown: Live, Beta, Deprecated
- [ ] Release date field
- [ ] Add planned feature: name "Advanced Filtering"
- [ ] Status dropdown: Planned, In Progress, Blocked
- [ ] Target date field
- [ ] Priority dropdown: P0-P3
- [ ] Click "Continue"

### B8. Step 7: Teams
- [ ] Progress bar shows "Step 7 of 8"
- [ ] Click "Add team"
- [ ] Name: "Payments Team"
- [ ] Lead: "Mike Rodriguez"
- [ ] Owns product areas: multi-select showing areas from Step 2
- [ ] Size: 6
- [ ] Slack channel: "#team-payments"
- [ ] Add second team
- [ ] Click "Continue"

### B9. Step 8: Tech Stack
- [ ] Progress bar shows "Step 8 of 8"
- [ ] Click "Add technology"
- [ ] Category dropdown: Frontend, Backend, Database, Infrastructure, Monitoring, Other
- [ ] Select "Frontend", technology: "React 18", notes: "With Vite"
- [ ] Add another: "Backend", "FastAPI", "Python 3.11"
- [ ] Add another: "Database", "Elasticsearch", "Elastic Cloud"
- [ ] Click "Finish"

### B10. Wizard Complete
- [ ] "Product setup complete!" message shown
- [ ] "Go to Dashboard" button visible
- [ ] "Continue to feedback upload" visible but disabled/grayed (Phase 3)
- [ ] Click "Go to Dashboard" → navigates to /dashboard

---

## C. Returning User Behavior

- [ ] Close browser, reopen, go to http://localhost:3000
- [ ] Log in with the same account
- [ ] Goes directly to /dashboard (NOT onboarding again)
- [ ] Refresh /dashboard → stays on dashboard

---

## D. Settings > Product Wizard (Edit Mode)

### D1. Navigate to Settings
- [ ] Click "Settings" in sidebar
- [ ] See sub-tabs: Product Wizard, Data Upload, Connectors, Account, Elasticsearch
- [ ] Click "Product Wizard" tab

### D2. Saved Data Pre-filled
- [ ] All data from onboarding wizard is pre-filled
- [ ] Product name shows "Test Product"
- [ ] Areas show the areas you added
- [ ] Goals show with correct linked areas
- [ ] Segments show (including defaults you edited)
- [ ] Competitors show
- [ ] Roadmap features show
- [ ] Teams show with correct area assignments
- [ ] Tech stack shows

### D3. Edit and Save
- [ ] Change product name to "Test Product Updated"
- [ ] Click Save → success feedback (toast or message)
- [ ] Refresh page → still shows "Test Product Updated"
- [ ] Add a new product area: "Billing"
- [ ] Save → success
- [ ] Go to Goals → linked area dropdown now includes "Billing"
- [ ] Delete a competitor → save → success → refresh → competitor gone

### D4. Partial Data
- [ ] Delete ALL areas (clear the list) → save → no error (empty list is valid)
- [ ] Delete ALL goals → save → no error
- [ ] GET /product/context still works (returns partial data, not error)

---

## E. API Verification (optional — use browser devtools or curl)

### E1. Wizard Endpoints
- [ ] `GET /api/v1/product/wizard` → returns all saved sections
- [ ] Response has `completed_sections` array listing which sections have data
- [ ] `GET /api/v1/product/wizard/basics` → returns basics section data
- [ ] `GET /api/v1/product/wizard/nonexistent` → 404
- [ ] `PUT /api/v1/product/wizard/basics` with `{"product_name": "Changed"}` → 200, updated
- [ ] `DELETE /api/v1/product/wizard/competitors` → 200, section removed
- [ ] `GET /api/v1/product/wizard` → competitors no longer in response

### E2. Product Context Endpoint
- [ ] `GET /api/v1/product/context` → returns flattened data
- [ ] Response includes: product_name, areas list, goals list, segments, competitors, etc.
- [ ] Empty sections return empty arrays (not errors or missing keys)

### E3. Onboarding Status
- [ ] `GET /api/v1/product/onboarding-status` → `{ "completed": true }`
- [ ] For the user who skipped: also shows `completed: true`

### E4. Auth Required
- [ ] Call any endpoint without JWT → 401
- [ ] Call with invalid JWT → 401

### E5. Multi-Tenant Isolation
- [ ] Log in as User A (Org A) → save wizard data
- [ ] Log in as User B (Org B) → GET /product/wizard → empty (no Org A data)
- [ ] User B saves their own wizard data
- [ ] Log back in as User A → only sees Org A data

---

## F. Elasticsearch Verification

- [ ] Open Kibana (or use Dev Tools / curl)
- [ ] Check index exists: `{org_id}-product-context`
- [ ] Query: `GET {org_id}-product-context/_search` → see 8 (or fewer) documents
- [ ] Each document has: id, org_id, section, data, created_at, updated_at
- [ ] Organizations index: org document has `onboarding_completed: true`

---

## G. Edge Cases

- [ ] Refresh browser mid-wizard (e.g., on Step 4) → comes back to Step 1 or last saved step (doesn't lose saved data)
- [ ] Fill Step 1, skip Steps 2-7, fill Step 8 → both saved, Steps 2-7 just don't exist
- [ ] Enter very long text in description (500+ chars) → no crash, saves correctly
- [ ] Add 20+ product areas → all saved, UI doesn't break
- [ ] Enter special characters in product name (& < > " ' /) → handles correctly
- [ ] Enter emoji in description → handles correctly or gracefully rejects
- [ ] Open Settings wizard in two browser tabs → both load data, saving in one doesn't break the other

---

## H. UI/UX Quality

- [ ] Dark mode works on ALL wizard screens (no white backgrounds)
- [ ] Light mode works on ALL wizard screens (toggle to check)
- [ ] Progress bar visually updates each step
- [ ] Completed steps show checkmark or filled dot in progress bar
- [ ] Form fields have proper labels
- [ ] Required fields have asterisk or "required" indicator
- [ ] Validation errors show below the specific field (not generic alert)
- [ ] "Continue" / "Skip" / "Back" buttons are clearly distinguishable
- [ ] Dropdowns are properly styled in dark mode
- [ ] No layout shift when adding/removing list items
- [ ] Loading indicator while data saves
- [ ] Agent chat bubble still visible on onboarding/wizard pages

---

## I. Backend Tests

- [x] Run backend test suite: `docker compose run --rm backend python -m pytest app/tests -v`
- [x] All Phase 1 tests still pass
- [x] All Phase 2 tests pass:
  - [x] test_product_service.py (9 tests)
  - [x] test_product_routes.py (12 tests)
  - [x] test_wizard_validation.py (8 tests)
- [x] No test failures (1 deprecation warning: HTTP_422_UNPROCESSABLE_ENTITY)

---

## J. Frontend Build

- [x] No TypeScript errors: `docker compose run --rm frontend npm run build`
- [ ] No console errors in browser dev tools during normal usage
- [ ] No console warnings about missing keys, uncontrolled inputs, etc.

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| A. Onboarding Flow | 10 | [ ] manual |
| B. Wizard Steps | 50+ | [ ] manual |
| C. Returning User | 4 | [ ] manual |
| D. Settings Wizard | 12 | [ ] manual |
| E. API Verification | 12 | [ ] optional |
| F. Elasticsearch | 5 | [ ] optional |
| G. Edge Cases | 7 | [ ] manual |
| H. UI/UX Quality | 13 | [ ] manual |
| I. Backend Tests | 5 | [x] verified |
| J. Frontend Build | 3 | [x] build OK, [ ] browser |
| **TOTAL** | **~120** | |

**Phase 2 is DONE when every box above is checked.**

Run: `docker compose up -d` then visit http://localhost:3000 to test manually.
