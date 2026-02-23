# Phase 4 Checklist — Search + Feedback Detail + Customer Profiles

> Walk through EVERY item below after Cursor finishes Phase 4.
> You need data from Phase 3 (feedback + customers) already in the system.
> If you don't have data, import the test CSVs from the Phase 3 checklist first.

---

## Pre-Check: Phases 1-3 Still Work

- [ ] `docker compose up` starts without errors
- [ ] Log in → dashboard
- [ ] Sidebar nav works
- [ ] Settings > Product Wizard → data intact
- [ ] Feedback page shows previously imported items
- [ ] Customers page shows previously imported customers
- [ ] Settings > Data Upload → upload history intact
- [ ] Can still upload a new feedback item manually
- [ ] Can still upload a new customer manually
- [ ] Dark/light theme works
- [ ] Agent bubble visible

---

## A. Semantic Search — Core Functionality

### A1. Basic Search
- [ ] Go to Feedback page
- [ ] See search bar at top: placeholder says something like "Search feedback..."
- [ ] Type "payment" → results appear (debounced, not instant per keystroke)
- [ ] Results include items containing "payment" in text
- [ ] Clear button (X) on search bar works → clears query, shows all items

### A2. Semantic Search (the magic)
- [ ] Type "payment problems"
- [ ] Results include "checkout broken" or "credit card declined" even though those words aren't "payment problems"
- [ ] Type "slow performance"
- [ ] Results include feedback about "dashboard crashes" or "search is slow" (semantic match)
- [ ] Type "unhappy enterprise customers"
- [ ] Results show negative feedback from enterprise segment

### A3. Empty Search
- [ ] Clear search bar completely (empty query)
- [ ] All feedback items shown, sorted by newest first
- [ ] No errors

### A4. No Results
- [ ] Type something that matches nothing: "xyzzy quantum blockchain"
- [ ] Shows "No results found" or similar message (not a crash)
- [ ] Search count shows 0

### A5. Search Performance
- [ ] Search results appear within 1-3 seconds (not 10+)
- [ ] Typing fast doesn't fire a request per keystroke (debounce working)
- [ ] No flickering or duplicate requests visible in network tab

---

## B. Filters

### B1. Product Area Filter
- [ ] Product area multi-select dropdown visible below search
- [ ] Dropdown populated with areas from your product wizard
- [ ] Select one area (e.g., "checkout") → only feedback with that area shown
- [ ] Select multiple areas → items from ANY selected area shown (OR logic within filter)
- [ ] Deselect all → all items shown again

### B2. Source Filter
- [ ] Source multi-select dropdown visible
- [ ] Shows all 11 source types with colored dots
- [ ] Select "support_ticket" → only support ticket items shown
- [ ] Select "support_ticket" + "app_store_review" → items from both shown
- [ ] Deselect all → all items

### B3. Sentiment Filter
- [ ] Sentiment toggle buttons visible: Positive / Negative / Neutral / All
- [ ] Click "Negative" → only negative sentiment items
- [ ] Click "Positive" → only positive
- [ ] Click "Neutral" → only neutral
- [ ] Click "All" → all items (default)

### B4. Segment Filter
- [ ] Customer segment dropdown visible
- [ ] Populated from product wizard segments (enterprise, smb, etc.)
- [ ] Select "enterprise" → only feedback from enterprise customers
- [ ] Feedback without a customer still shows when "All" selected

### B5. Date Range Filter
- [ ] Date range presets visible: 7d / 30d / 90d
- [ ] Click "7d" → only feedback from last 7 days
- [ ] Click "30d" → last 30 days
- [ ] Custom date picker works → select specific from/to dates → filtered
- [ ] Clear date filter → all dates

### B6. Customer Filter
- [ ] Customer search/autocomplete input visible
- [ ] Type "Tech" → autocomplete suggests "TechFlow Inc"
- [ ] Select "TechFlow Inc" → only TechFlow's feedback shown

### B7. Has Customer Filter
- [ ] Toggle: All / Linked / Unlinked
- [ ] "Linked" → only feedback with a customer_id attached
- [ ] "Unlinked" → only feedback without a customer
- [ ] "All" → everything

### B8. Combined Filters
- [ ] Set source = "support_ticket" AND sentiment = "Negative"
- [ ] Only negative support tickets shown
- [ ] Add product area = "checkout"
- [ ] Further narrows results (AND logic between different filters)
- [ ] Result count updates correctly

### B9. Clear All Filters
- [ ] "Clear all filters" link visible
- [ ] Click → all filters reset, search cleared, all items shown

---

## C. Filter State in URL

### C1. URL Updates
- [ ] Type "payment" in search → URL changes to include `?q=payment`
- [ ] Select source filter → URL adds `&source=support_ticket`
- [ ] Select sentiment → URL adds `&sentiment=negative`
- [ ] Full example: `/feedback?q=payment&source=support_ticket&sentiment=negative`

### C2. URL Persistence
- [ ] Apply filters → copy the URL
- [ ] Open new browser tab → paste URL → same filters applied, same results
- [ ] Refresh page → filters still active (not reset)

### C3. Shareable
- [ ] Copy filtered URL → open in incognito (log in first) → same view
- [ ] Bookmark a filtered view → later click bookmark → filters restored

---

## D. Results List

### D1. Card Display
- [ ] Each result shows: text preview (2 lines, truncated with "...")
- [ ] Source badge (colored pill — different color per source type)
- [ ] Sentiment dot: green (positive), red (negative), gray (neutral) + score
- [ ] Product area tag
- [ ] Customer name (if linked)
- [ ] Date (relative: "2 days ago", "1 month ago")

### D2. Result Count
- [ ] Top of results: "Showing X results" (or "X of Y")
- [ ] Count updates when filters change

### D3. Sorting
- [ ] Sort dropdown visible: Relevance / Date / Sentiment
- [ ] When searching: default sort is "Relevance" (best matches first)
- [ ] When not searching: default sort is "Date" (newest first)
- [ ] Switch to "Sentiment (most negative)" → most negative items first
- [ ] Switch to "Date (newest)" → chronological

### D4. Pagination
- [ ] If >20 results: pagination controls or "Load more" button visible
- [ ] Click next page / load more → additional items shown
- [ ] Page changes work with filters active

---

## E. Feedback Detail Slide-Out

### E1. Open/Close
- [ ] Click any feedback item in the list → right panel slides in from right
- [ ] Panel takes ~30% width on desktop
- [ ] List (left side) is still visible but narrower
- [ ] Close: click X button → panel closes
- [ ] Close: click outside panel → panel closes
- [ ] Close: press Escape key → panel closes

### E2. Full Content
- [ ] Full feedback text shown (untruncated — full text visible)
- [ ] Source badge (larger than in list)
- [ ] Date displayed
- [ ] Sentiment: colored badge + score (e.g., "Negative -0.72")
- [ ] Product area tag
- [ ] Rating shown as stars (if item has rating)
- [ ] Author name + email (if available)
- [ ] Ingestion info: "Imported via CSV on Feb 10, 2026" or "Added manually"

### E3. Customer Card
- [ ] If feedback has a linked customer: customer card visible
- [ ] Card shows: company name, segment badge, MRR, ARR
- [ ] Health score (color-coded)
- [ ] Account manager name
- [ ] Renewal date (warning icon if within 60 days)
- [ ] Company name is clickable → navigates to /customers/{id}

### E4. No Customer
- [ ] If feedback has NO linked customer: customer card section hidden or shows "No customer linked"

### E5. Similar Feedback
- [ ] "Similar items" section visible
- [ ] Shows up to 5 similar feedback items
- [ ] Each similar item: text preview (1 line), sentiment dot, date
- [ ] Click a similar item → detail panel swaps to show THAT item
- [ ] Original item is no longer shown, new item is
- [ ] Can keep clicking similar items to navigate through related feedback

### E6. Actions
- [ ] "Ask agent" button visible (placeholder — doesn't need to work yet, just exists)
- [ ] "Generate spec" button visible (placeholder)
- [ ] "Copy text" button → copies feedback text to clipboard
- [ ] "Star" / bookmark button → toggles saved state (visual change, stored in localStorage)

### E7. Multiple Items
- [ ] Click item A → panel shows A
- [ ] Click item B (in list, without closing) → panel updates to show B
- [ ] Close panel → click item C → panel reopens with C

---

## F. Customer List Page (Full)

### F1. Search
- [ ] Search input at top of customers page
- [ ] Type "Tech" → filters to "TechFlow Inc" and "GlobalTech"
- [ ] Type "Sarah" → filters to customers with account manager "Sarah Chen"
- [ ] Clear search → all customers shown

### F2. Filters
- [ ] Segment multi-select dropdown → select "enterprise" → only enterprise shown
- [ ] Health score range slider → set 0-50 → only low-health customers
- [ ] Renewal filter: "within 30d" → only customers renewing within 30 days
- [ ] Has negative feedback toggle → "Yes" → only customers with negative feedback
- [ ] ARR range inputs → set min 20000, max 50000 → filtered
- [ ] Combine multiple filters → AND logic

### F3. Table
- [ ] Columns: Company Name, Segment, MRR, ARR, Health, Feedback Count, Renewal
- [ ] Click column header → sorts by that column
- [ ] Click again → reverse sort
- [ ] Health column color-coded:
  - [ ] Green for score 70+ (e.g., MegaCorp 91)
  - [ ] Yellow for 40-69 (e.g., TechFlow 72, SmallBiz 60)
  - [ ] Red for <40 (e.g., StartupX 30)
- [ ] Renewal column: warning icon on dates within 60 days of today
- [ ] Feedback count shows number with negative count (e.g., "12 (5 negative)")
- [ ] Click any row → navigates to /customers/{id}

### F4. Pagination
- [ ] Pagination controls if >20 customers

---

## G. Customer Profile Page

### G1. Navigation
- [ ] Click customer row in list → URL changes to /customers/{id}
- [ ] Page loads with full customer profile
- [ ] Browser back button → returns to customer list

### G2. Header
- [ ] Company name large and prominent
- [ ] Segment badge (e.g., "Enterprise" in colored pill)
- [ ] Plan name shown (if available)
- [ ] Industry tag shown

### G3. Key Metrics Cards
- [ ] Row of metric cards: MRR, ARR, Health Score, Total Feedback, Avg Sentiment, Days to Renewal
- [ ] MRR shows dollar amount (e.g., "$2,500")
- [ ] ARR shows dollar amount
- [ ] Health score: number + color coding
- [ ] Total feedback: count of all feedback from this customer
- [ ] Avg sentiment: score with color
- [ ] Days to renewal: number, highlighted/warning if <60

### G4. Account Details
- [ ] Account manager name
- [ ] Employee count
- [ ] Created date
- [ ] Renewal date (highlighted if within 60 days)
- [ ] Plan/tier name
- [ ] External customer ID (if imported from CSV)

### G5. Sentiment Trend Chart
- [ ] Line chart visible
- [ ] X-axis: time periods (months or weeks)
- [ ] Y-axis: sentiment score (-1 to 1)
- [ ] Line showing this customer's avg sentiment per period
- [ ] Second line (overlay): product-wide average for comparison
- [ ] Legend: "TechFlow Inc" vs "Product Average"
- [ ] If customer has only 1 data point → chart shows single point (no crash)
- [ ] If customer has 0 feedback → chart shows "No data" or is hidden

### G6. Feedback History
- [ ] All feedback from this customer listed below chart
- [ ] Same card format as feedback page (text, source badge, sentiment, date)
- [ ] If many items: pagination or load more
- [ ] Filter by product area works within this customer's feedback
- [ ] Filter by sentiment works
- [ ] Click feedback item → opens detail (slide-out or modal)

### G7. Specs Section
- [ ] "Specs Mentioning This Customer" section visible
- [ ] Shows placeholder: "Coming in Phase 6" (or empty state)

### G8. Actions
- [ ] "Ask agent about this customer" button → placeholder (exists but non-functional)
- [ ] "View all feedback" link → navigates to /feedback?customer={customer_id}
- [ ] Verify: feedback page loads with customer filter pre-applied
- [ ] "View in Kibana" → placeholder (exists but non-functional)

### G9. Profile for Different Customer Types
- [ ] Check enterprise customer (full data) → all fields shown
- [ ] Check trial customer (minimal data, $0 MRR) → handles gracefully, no crash
- [ ] Check customer with 0 feedback → no chart crash, shows "No feedback yet"
- [ ] Check customer with many feedback items → loads without timeout

---

## H. Cross-Page Navigation

- [ ] Feedback list → click customer name in card → customer profile page
- [ ] Customer profile → "View all feedback" → feedback page filtered by customer
- [ ] Feedback page (filtered by customer) → clear filter → all feedback
- [ ] Customer profile → browser back → customer list
- [ ] Feedback detail slide-out → click customer card company name → customer profile
- [ ] Customer list → click row → customer profile → back → customer list (filters preserved)

---

## I. API Verification (curl or devtools)

### I1. Search Endpoint
- [ ] `POST /api/v1/search/feedback` with `{"query": "payment"}` → 200 with results
- [ ] Results include items semantically related to "payment" (not just keyword match)
- [ ] `POST /api/v1/search/feedback` with `{"query": ""}` → 200, all items sorted by date
- [ ] `POST /api/v1/search/feedback` with filters → filtered results
- [ ] Response has `data` array + `pagination` object + `query` field

### I2. Similar Endpoint
- [ ] `GET /api/v1/feedback/{id}/similar` → 200, returns up to 5 items
- [ ] Returned items do NOT include the source item
- [ ] Items are semantically related to the source

### I3. Customer Feedback Endpoint
- [ ] `GET /api/v1/customers/{id}/feedback` → 200, only that customer's feedback
- [ ] Supports pagination params

### I4. Sentiment Trend Endpoint
- [ ] `GET /api/v1/customers/{id}/sentiment-trend` → 200
- [ ] Response has `periods` array with `date`, `avg_sentiment`, `count`
- [ ] Response has `product_average` array for comparison overlay
- [ ] Customer with 0 feedback → empty periods array (not error)

### I5. Auth + Multi-Tenant
- [ ] All endpoints without JWT → 401
- [ ] Search only returns current org's feedback
- [ ] Customer endpoints only return current org's customers
- [ ] Log in as Org B → search returns nothing from Org A

---

## J. ELSER Verification

- [ ] Open Kibana Dev Tools
- [ ] Run a semantic query against `{org_id}-feedback`:
```json
GET {org_id}-feedback/_search
{
  "query": {
    "semantic": {
      "field": "text_semantic",
      "query": "payment issues"
    }
  },
  "size": 5
}
```
- [ ] Returns results with relevance scores
- [ ] Results include items that don't contain "payment" literally but are semantically related
- [ ] Scores vary (not all the same)

---

## K. Edge Cases

- [ ] Search with very long query (100+ characters) → no crash, returns results or empty
- [ ] Search with special characters (& < > " ') → no crash
- [ ] Search with emoji → no crash
- [ ] Filter by product area that has 0 feedback → empty results, no crash
- [ ] Filter by date range that excludes all data → empty results
- [ ] Click similar item that was deleted → graceful error
- [ ] Customer with 500+ feedback items → profile loads (may paginate), no timeout
- [ ] Open detail panel → resize browser window → panel stays usable
- [ ] Open detail panel → switch to different page via sidebar → panel closes, page loads

---

## L. UI/UX Quality

### L1. Search & Filters
- [ ] Search bar is prominent and visually clear
- [ ] Placeholder text helpful
- [ ] Filter dropdowns styled correctly in dark mode
- [ ] Active filters visually indicated (highlighted, count badge)
- [ ] "Clear all filters" only appears when filters are active

### L2. Detail Panel
- [ ] Smooth slide-in animation (not instant jump)
- [ ] Panel doesn't overlap sidebar
- [ ] Scrollable if content exceeds viewport
- [ ] Dark mode: all elements readable, no white boxes
- [ ] Light mode: all elements readable

### L3. Customer Profile
- [ ] Clean layout, card-based metrics
- [ ] Chart renders correctly in dark mode (axis labels visible)
- [ ] Chart renders correctly in light mode
- [ ] Health score badge colors consistent with list page
- [ ] Renewal warning consistent with list page

### L4. General
- [ ] Loading skeletons while data fetches (search, profile, chart)
- [ ] No layout shift when results load
- [ ] Source badge colors consistent between list, detail, and customer profile
- [ ] Agent chat bubble still visible on all pages
- [ ] All new pages work in both dark and light mode

---

## M. Backend Tests

- [ ] Run: `docker compose exec backend pytest`
- [ ] All Phase 1 tests pass
- [ ] All Phase 2 tests pass
- [ ] All Phase 3 tests pass
- [ ] All Phase 4 tests pass:
  - [ ] test_search_service.py (9 tests)
  - [ ] test_similar.py (4 tests)
  - [ ] test_customer_profile.py (4 tests)
  - [ ] test_search_routes.py (6 tests)
- [ ] No test failures

---

## N. Frontend Build

- [ ] No TypeScript errors: `docker compose exec frontend npx tsc --noEmit`
- [ ] No console errors during normal usage
- [ ] No React warnings (missing keys, uncontrolled inputs)

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| Pre-Check (Phases 1-3) | 11 | [ ] |
| A. Semantic Search | 12 | [ ] |
| B. Filters | 25 | [ ] |
| C. URL Filter State | 5 | [ ] |
| D. Results List | 10 | [ ] |
| E. Detail Slide-Out | 22 | [ ] |
| F. Customer List | 16 | [ ] |
| G. Customer Profile | 28 | [ ] |
| H. Cross-Page Navigation | 6 | [ ] |
| I. API Verification | 12 | [ ] |
| J. ELSER Verification | 4 | [ ] |
| K. Edge Cases | 9 | [ ] |
| L. UI/UX Quality | 14 | [ ] |
| M. Backend Tests | 6 | [ ] |
| N. Frontend Build | 3 | [ ] |
| **TOTAL** | **~183** | |

**Phase 4 is DONE when every box above is checked.**
