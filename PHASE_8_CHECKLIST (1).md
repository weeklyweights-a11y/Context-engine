# Phase 8 Checklist — Polish + Ship

> Walk through EVERY item below after Cursor finishes Phase 8.
> This is the FINAL checklist. After this, the product is complete.
> Section N is the end-to-end test: a fresh user goes through the entire product.

---

## Pre-Check: Phases 1-7 Still Work

- [ ] `docker compose up` starts without errors
- [ ] Log in → full dashboard with 9 widgets
- [ ] Feedback search + filters + detail slide-out work
- [ ] Customer profiles + sentiment chart work
- [ ] Agent chat with all 7 tools works
- [ ] Specs generation + 4-tab viewer works
- [ ] Analytics page works
- [ ] Product wizard in settings works

---

## A. Settings > Connectors — Slack Integration

### A1. Connect Flow
- [ ] Go to Settings > Connectors
- [ ] "Connect Slack" button visible with Slack icon
- [ ] Click → redirects to Slack OAuth authorization page
- [ ] Approve in Slack → callback redirects back to Settings
- [ ] Settings now shows: "Connected to [workspace name]"

### A2. Channel Selection
- [ ] Channel list loads showing available Slack channels
- [ ] Each channel has a toggle (on/off)
- [ ] Toggle on "general" → channel becomes monitored
- [ ] Toggle on a second channel → also monitored
- [ ] Toggle off "general" → channel no longer monitored
- [ ] Save → changes persisted

### A3. Message Ingestion
- [ ] Post a message in a monitored Slack channel
- [ ] Wait 10-30 seconds
- [ ] Go to Feedback page → new item appears
- [ ] Source shows "Slack Message"
- [ ] Author matches Slack user who posted
- [ ] Sentiment auto-analyzed
- [ ] Ingestion method shows "slack_connector"

### A4. Deduplication
- [ ] Same Slack message doesn't create duplicate feedback items
- [ ] Edit a Slack message → original feedback unchanged (edits ignored)

### A5. Bot Messages Ignored
- [ ] Bot posts a message in channel → no feedback item created
- [ ] Only human messages create feedback

### A6. Disconnect
- [ ] Click "Disconnect" → confirmation dialog
- [ ] Confirm → connection removed
- [ ] Settings shows "Connect Slack" button again
- [ ] Monitored channels stop creating feedback items

### A7. Future Connectors
- [ ] Below Slack: "Coming Soon" cards visible
- [ ] Zendesk, Intercom, Jira, Linear shown as greyed-out
- [ ] Each has "Notify me" or similar placeholder button

### A8. No Slack Credentials
- [ ] If SLACK_CLIENT_ID not set in .env: "Connect Slack" shows message about configuration needed (not crash)

---

## B. Settings > Account

### B1. Profile
- [ ] Email displayed (read-only, not editable)
- [ ] Full name field: shows current name
- [ ] Edit name → save → success toast
- [ ] Refresh → new name persisted

### B2. Change Password
- [ ] Current password field
- [ ] New password field + confirm new password field
- [ ] Submit with correct current password → success
- [ ] Submit with wrong current password → error: "Current password incorrect"
- [ ] Submit with mismatched new passwords → validation error
- [ ] After password change: can log out and log in with new password
- [ ] Old password no longer works

### B3. Organization
- [ ] Organization name field shows current org name
- [ ] Edit → save → success
- [ ] Refresh → new org name shown

### B4. Theme
- [ ] Theme toggle present (may already exist from Phase 1)
- [ ] Dark ↔ light works from this settings page

### B5. Delete Account
- [ ] "Delete Account" button visible (red/destructive styling)
- [ ] Click → confirmation dialog: "Type DELETE to confirm"
- [ ] Type "DELETE" → confirm → account deleted
- [ ] Redirected to /login
- [ ] Cannot log in with deleted credentials
- [ ] All org data removed from Elasticsearch (verify in Kibana if possible)

### B6. Delete Account — Cancel
- [ ] Open delete dialog → close without typing DELETE → nothing happens
- [ ] Type something other than "DELETE" → submit button disabled or shows error

---

## C. Settings > Elasticsearch

### C1. Connection Status
- [ ] Green indicator: "Connected"
- [ ] Cluster name displayed
- [ ] Cluster version displayed (8.x)

### C2. Index Stats Table
- [ ] Table shows all org indexes:
  - [ ] {org_id}-feedback: document count + size
  - [ ] {org_id}-customers: document count + size
  - [ ] {org_id}-product-context: document count + size
  - [ ] {org_id}-specs: document count + size
  - [ ] {org_id}-conversations: document count + size
- [ ] Counts match reality (verify 1-2 against Kibana)

### C3. Re-index
- [ ] "Re-index all" button visible
- [ ] Click → confirmation → processing indicator
- [ ] Completes without error
- [ ] Data still accessible after re-index

### C4. Clear Data
- [ ] "Clear all data" button (red/destructive)
- [ ] Click → "Type DELETE to confirm"
- [ ] Confirm → all org data removed
- [ ] Dashboard shows empty state
- [ ] Feedback page shows empty state
- [ ] Customers page shows empty state
- [ ] Specs page shows empty state

### C5. Kibana Link
- [ ] "Open Kibana" link/button visible
- [ ] Click → opens Kibana in new tab

---

## D. Responsive — Tablet (resize browser to 768-1200px)

- [ ] Sidebar collapses to icon-only mode (~64px wide)
- [ ] Icons visible for each nav item
- [ ] Hover icon → tooltip shows page name
- [ ] Click icon → navigates to page
- [ ] Dashboard: single column layout (widgets stack)
- [ ] Agent chat: overlays content (not side-by-side)
- [ ] Tables: horizontal scroll if columns overflow
- [ ] Feedback detail slide-out: still works (may be wider relative to screen)
- [ ] Customer profile: still readable
- [ ] All pages functional at tablet width

---

## E. Responsive — Mobile (resize to <768px)

- [ ] Sidebar replaced by hamburger menu (☰)
- [ ] Click hamburger → sidebar slides out as overlay
- [ ] Click nav item → navigates + sidebar closes
- [ ] Dashboard: single column, simplified cards
- [ ] Agent chat: full-screen overlay when opened
- [ ] Tables → card view or horizontal scroll
- [ ] Feedback page: search + results usable
- [ ] Login / signup pages work on mobile
- [ ] No horizontal overflow (no sideways scrolling on body)
- [ ] Functional but not pixel-perfect (acceptable)

---

## F. Error Handling — All Pages

### F1. Toast Notifications
- [ ] Success action (save wizard step) → green toast, auto-dismiss ~3 seconds
- [ ] Error action (API failure) → red toast, persistent until dismissed
- [ ] Info message → blue toast, auto-dismiss ~5 seconds

### F2. Network Error
- [ ] Disconnect internet → try an action → "Unable to connect" message
- [ ] Reconnect → retry works

### F3. API Errors
- [ ] Trigger a 404 (go to /specs/nonexistent-id) → "This item doesn't exist"
- [ ] Trigger a 422 (submit form with bad data) → field-specific error below input
- [ ] Trigger a 500 (if possible) → "Something went wrong. Please try again."

### F4. ES Connection Error
- [ ] If ES goes down → dashboard shows meaningful error (not blank/crash)
- [ ] Settings > Elasticsearch shows red "Disconnected" indicator

---

## G. Loading States — All Pages

- [ ] Dashboard: 9 skeleton widgets on first load
- [ ] Feedback page: skeleton rows while search runs
- [ ] Feedback detail: skeleton content while loading
- [ ] Customer list: skeleton table rows
- [ ] Customer profile: skeleton header + metric cards
- [ ] Specs list: skeleton cards
- [ ] Spec detail: skeleton content while loading
- [ ] Agent chat: typing indicator while processing
- [ ] Settings tabs: skeleton forms while loading
- [ ] Analytics page: skeleton charts
- [ ] No blank/white flashes on any page

---

## H. Empty States — All Pages

Log in as a BRAND NEW user (no data):

- [ ] Dashboard: "No data yet. Set up your product and upload feedback." + [Start Product Wizard] + [Upload Feedback]
- [ ] Feedback: "No feedback yet. Import data to start analyzing." + [Upload CSV] + [Add Manually]
- [ ] Customers: "No customers yet. Upload data to connect feedback to revenue." + [Upload Customers]
- [ ] Specs: "No specs yet. Ask the agent to create your first spec." + [Open Agent Chat]
- [ ] Analytics: "Dashboards appear once you have feedback data." + [Upload Feedback]
- [ ] Agent chat (empty): 6 suggested prompt chips visible
- [ ] CTA buttons actually navigate to the correct pages

---

## I. README.md

- [ ] README.md exists in project root
- [ ] Has "Quick Start" section with: clone, configure .env, docker compose up
- [ ] .env.example file exists with all required variables listed
- [ ] Architecture overview (React → FastAPI → Elasticsearch)
- [ ] Features list
- [ ] Tech stack listed
- [ ] Development section (how to run tests)
- [ ] Following README from scratch: can get the app running

---

## J. Demo Script

- [ ] docs/demo_script.md exists
- [ ] 8-minute walkthrough documented
- [ ] Step-by-step with what to click and what to say
- [ ] Every step in demo script actually works when followed

---

## K. API Verification (curl or devtools)

### K1. Account Endpoints
- [ ] `PUT /api/v1/auth/profile` with `{"full_name": "New Name"}` → 200
- [ ] `PUT /api/v1/auth/password` with correct current + new → 200
- [ ] `PUT /api/v1/auth/password` with wrong current → 401
- [ ] `PUT /api/v1/auth/org` with `{"name": "New Org"}` → 200
- [ ] `DELETE /api/v1/auth/account` with `{"confirm": "DELETE"}` → 200

### K2. Admin Endpoints
- [ ] `GET /api/v1/admin/index-stats` → 200, index list with counts
- [ ] `DELETE /api/v1/admin/clear-data` with confirm → 200

### K3. Slack Endpoints (if Slack configured)
- [ ] `GET /api/v1/slack/status` → 200, connection info or "not connected"
- [ ] `GET /api/v1/slack/channels` → 200, channel list (if connected)

### K4. Auth + Multi-Tenant
- [ ] All new endpoints require JWT
- [ ] All isolate by org_id

---

## L. Edge Cases

- [ ] Delete account → sign up with SAME email → works (fresh account)
- [ ] Clear all data → upload new data → everything works fresh
- [ ] Rapidly toggle theme 10 times → no crash
- [ ] Open Settings while agent is processing → no interference
- [ ] Change org name → reflected in sidebar/header (if shown anywhere)
- [ ] Slack webhook with malformed payload → rejected, no crash
- [ ] Slack webhook without valid signing secret → rejected (401/403)

---

## M. Backend Tests

- [ ] Run: `docker compose exec backend pytest`
- [ ] All Phase 1-7 tests still pass
- [ ] All Phase 8 tests pass:
  - [ ] test_slack_service.py (8 tests)
  - [ ] test_account_routes.py (6 tests)
  - [ ] test_admin_routes.py (4 tests)
- [ ] No test failures
- [ ] **TOTAL TEST COUNT:** all tests across all 8 phases pass in single run

---

## N. End-to-End: The Full Loop

> This is the ultimate test. A fresh user. Zero data. Walk through the entire product.

### N1. Fresh Start
- [ ] `docker compose down && docker compose up` (fresh containers)
- [ ] Open http://localhost:3000

### N2. Sign Up
- [ ] Create account: email, password, org name
- [ ] Redirected to /onboarding

### N3. Onboarding — Product Wizard
- [ ] Complete at least Steps 1-3 (Basics, Areas, Goals)
- [ ] Skip remaining steps
- [ ] Continue to feedback upload

### N4. Upload Feedback
- [ ] Upload a CSV with 10+ feedback items
- [ ] Column mapping works
- [ ] Import completes successfully
- [ ] Items appear in feedback list

### N5. Upload Customers
- [ ] Upload a CSV with 5+ customers
- [ ] Import completes
- [ ] Customers appear in customer list

### N6. Finish Onboarding
- [ ] Complete onboarding → redirected to /dashboard

### N7. Dashboard
- [ ] 9 widgets show real data from your uploads
- [ ] Summary cards: non-zero numbers
- [ ] Charts render with data points

### N8. Feedback Search
- [ ] Search for a term in your data → semantic results
- [ ] Apply filters → correct filtering
- [ ] Click item → detail slide-out with customer card

### N9. Customer Profile
- [ ] Click customer name → profile page
- [ ] Metrics, sentiment chart, feedback history visible

### N10. Agent Chat
- [ ] Open agent chat
- [ ] "What are the top issues?" → agent analyzes with tools
- [ ] Agent cites specific numbers from your data
- [ ] Follow-up question → agent remembers context

### N11. Spec Generation
- [ ] "Generate specs for [topic from your data]"
- [ ] Agent gathers data → generates 4 docs
- [ ] Click [View Full Specs] → spec detail page
- [ ] All 4 tabs have real content with citations

### N12. Analytics
- [ ] Analytics page shows charts (or Kibana)
- [ ] Date range works

### N13. Settings
- [ ] Product Wizard → all saved data there
- [ ] Data Upload → upload history shows imports
- [ ] Elasticsearch → connected, index stats accurate
- [ ] Account → can change name

### N14. Full Loop Complete
- [ ] Every major feature tested in one session
- [ ] No crashes, no dead pages, no broken links
- [ ] **THE PRODUCT WORKS END TO END** ✅

---

## O. Frontend Build

- [ ] No TypeScript errors: `docker compose exec frontend npx tsc --noEmit`
- [ ] No console errors during full end-to-end test
- [ ] No React warnings

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| Pre-Check (Phases 1-7) | 8 | [ ] |
| A. Slack Integration | 16 | [ ] |
| B. Account Settings | 12 | [ ] |
| C. Elasticsearch Settings | 10 | [ ] |
| D. Responsive — Tablet | 10 | [ ] |
| E. Responsive — Mobile | 10 | [ ] |
| F. Error Handling | 7 | [ ] |
| G. Loading States | 11 | [ ] |
| H. Empty States | 7 | [ ] |
| I. README | 8 | [ ] |
| J. Demo Script | 4 | [ ] |
| K. API Verification | 9 | [ ] |
| L. Edge Cases | 7 | [ ] |
| M. Backend Tests | 5 | [ ] |
| N. **End-to-End** | 22 | [ ] |
| O. Frontend Build | 3 | [ ] |
| **TOTAL** | **~149** | |

**Phase 8 is DONE — and THE PRODUCT IS COMPLETE — when every box above is checked.**

---

## Congratulations

If you've checked every box in all 8 phase checklists, you have:

| Phase | Checkboxes |
|-------|-----------|
| Phase 1: Foundation | ~24 |
| Phase 2: Product Wizard | ~120 |
| Phase 3: Data Ingestion | ~170 |
| Phase 4: Search + Detail | ~183 |
| Phase 5: Agent + Tools | ~167 |
| Phase 6: Spec Generation | ~157 |
| Phase 7: Dashboard + Analytics | ~145 |
| Phase 8: Polish + Ship | ~149 |
| **TOTAL** | **~1,115** |

**Context Engine v2 is feature-complete.** 🚀
