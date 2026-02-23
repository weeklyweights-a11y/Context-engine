# Phase 7 Checklist — Dashboard + Analytics + Kibana

> Walk through EVERY item below after Cursor finishes Phase 7.
> You need: feedback + customer data (Phase 3), product wizard (Phase 2).
> More data = better dashboard. If you only have 10 items, charts will be sparse — that's OK, just verify they render.

---

## Pre-Check: Phases 1-6 Still Work

- [ ] `docker compose up` starts without errors
- [ ] Log in → dashboard (will now have widgets instead of empty state)
- [ ] Feedback search works
- [ ] Customer profiles work
- [ ] Agent chat works
- [ ] Specs page works with previously generated specs
- [ ] Settings > Product Wizard data intact

---

## A. Dashboard — Summary Cards (Widget 1)

### A1. Display
- [ ] Top row shows 4 cards
- [ ] Card 1: "Total Feedback" with number (e.g., 847)
- [ ] Card 2: "Avg Sentiment" with score (e.g., -0.23)
- [ ] Card 3: "Active Issues" with count
- [ ] Card 4: "At-Risk Customers" with count

### A2. Trend Indicators
- [ ] Each card shows trend arrow: ↑ or ↓
- [ ] Trend shows % change vs previous period (e.g., "↑12%")
- [ ] Positive trends: green arrow up (for feedback count, this could be neutral)
- [ ] Negative trends: red arrow down (for sentiment getting worse)

### A3. Clickable
- [ ] Click "Total Feedback" → navigates to /feedback
- [ ] Click "Avg Sentiment" → navigates to /feedback (or analytics)
- [ ] Click "Active Issues" → navigates to /feedback?sentiment=negative (or similar)
- [ ] Click "At-Risk Customers" → navigates to /customers?health_max=40

---

## B. Dashboard — Volume Chart (Widget 2)

- [ ] Line chart visible below summary cards
- [ ] X-axis: dates for the selected period
- [ ] Y-axis: feedback count
- [ ] Line shows feedback volume over time
- [ ] Toggle: can show/hide lines per product area
- [ ] Toggle "checkout" → checkout-specific line appears
- [ ] Toggle multiple areas → multiple lines with legend
- [ ] Hover over data point → tooltip shows exact count + date
- [ ] Click data point → navigates to /feedback filtered by that date

---

## C. Dashboard — Sentiment Donut (Widget 3)

- [ ] Donut/pie chart visible
- [ ] 3 segments: Positive (green), Negative (red), Neutral (gray)
- [ ] Percentages shown (sum to ~100%)
- [ ] Hover segment → shows exact count + percentage
- [ ] Click "Negative" segment → navigates to /feedback?sentiment=negative
- [ ] Click "Positive" segment → navigates to /feedback?sentiment=positive

---

## D. Dashboard — Top Issues (Widget 4)

- [ ] 3-5 ranked issue cards visible
- [ ] Each card shows:
  - [ ] Issue name (product area + theme)
  - [ ] Feedback count
  - [ ] Growth rate ("↑23% this week")
  - [ ] Severity badge: Critical / Emerging / Stable / Improving
  - [ ] Affected customers count
  - [ ] Total ARR affected
- [ ] "Investigate" button on each → opens agent chat with "Tell me about {issue}"
- [ ] "Generate Spec" button on each → opens agent chat with "Generate specs for {issue}"
- [ ] Issues ranked by impact (not just volume)

---

## E. Dashboard — Product Area Breakdown (Widget 5)

- [ ] Horizontal bar chart visible
- [ ] One bar per product area
- [ ] Bar length = feedback count
- [ ] Bar color reflects avg sentiment (green = positive, red = negative)
- [ ] Hover → shows area name, count, avg sentiment
- [ ] Click bar → navigates to /feedback?area={area}

---

## F. Dashboard — At-Risk Customers (Widget 6)

- [ ] Table with max 5 rows
- [ ] Columns: Company, ARR, Negative Feedback (30d), Renewal, Health
- [ ] Sorted by risk (lowest health first)
- [ ] Health column color-coded: green (70+), yellow (40-69), red (<40)
- [ ] Renewal column: warning icon if within 60 days
- [ ] Click row → navigates to /customers/{id}
- [ ] "View all" link → navigates to /customers?health_max=40

---

## G. Dashboard — Recent Feedback Stream (Widget 7)

- [ ] Latest 10 feedback items listed
- [ ] Each shows: text preview, source badge, sentiment dot, area tag, time ago
- [ ] Items sorted newest first
- [ ] Click item → navigates to feedback detail or /feedback?id={id}
- [ ] Auto-refresh works (every 30s) OR manual refresh button

---

## H. Dashboard — Source Distribution (Widget 8)

- [ ] Pie chart visible
- [ ] Slices per source type (support_ticket, app_store_review, etc.)
- [ ] Colors match source badge colors from feedback page
- [ ] Hover → shows source name, count, percentage
- [ ] Click slice → navigates to /feedback?source={type}

---

## I. Dashboard — Feedback by Segment (Widget 9)

- [ ] Grouped bar chart visible
- [ ] Groups by product area (or overall)
- [ ] Bars per segment: enterprise, SMB, consumer, trial
- [ ] Legend shows segment colors
- [ ] Hover → shows segment name + count
- [ ] Click bar → navigates to /feedback?segment={seg}&area={area}

---

## J. Date Range Selector

- [ ] Top bar of dashboard shows: [7d] [30d] [90d] [Custom]
- [ ] Default: 30d
- [ ] Click "7d" → ALL widgets update to show last 7 days data
- [ ] Click "90d" → all widgets update to 90-day view
- [ ] Custom → date picker appears → select range → widgets update
- [ ] Date range persists in URL: /dashboard?period=30d
- [ ] Refresh page → same period selected
- [ ] Summary card trends recalculate based on selected period

---

## K. Dashboard Customization

- [ ] "Customize Dashboard" button visible in top bar
- [ ] Click → dropdown with checkboxes for each of 9 widgets
- [ ] All checked by default
- [ ] Uncheck "Source Distribution" → widget disappears from dashboard
- [ ] Uncheck "At-Risk Customers" → table disappears
- [ ] Check them back → widgets reappear
- [ ] Preferences persist on page refresh
- [ ] Preferences persist on logout/login

---

## L. Dashboard — Refresh

- [ ] Refresh button (↻) in top bar
- [ ] Click → all widgets reload data
- [ ] Loading skeletons shown during refresh

---

## M. Dashboard — Empty State

- [ ] Log in as NEW user with no data
- [ ] Dashboard shows: "No data yet. Set up your product and upload feedback."
- [ ] CTAs: [Start Product Wizard] [Upload Feedback]
- [ ] No chart crashes or errors with 0 data
- [ ] Summary cards show 0 / 0 / 0 / 0 (not errors)

---

## N. Dashboard — Loading States

- [ ] On first load: 9 skeleton placeholders shown
- [ ] Skeletons match widget shapes (card skeletons, chart skeletons, table skeletons)
- [ ] No layout shift when real data loads in
- [ ] If one widget API fails: that widget shows error, others still load

---

## O. Analytics Page

### O1. Navigation
- [ ] Click "Analytics" in sidebar
- [ ] Analytics page loads with tabs

### O2. Tabs
- [ ] 4 sub-tabs visible: Feedback Overview / Trends & Alerts / Deep Dive / Custom
- [ ] Tab 1 (Feedback Overview): charts showing volume, sources, areas, sentiment
- [ ] Tab 2 (Trends & Alerts): sentiment by area over time, week-over-week
- [ ] Tab 3 (Deep Dive): filterable view of feedback items
- [ ] Tab 4 (Custom): "Open Kibana in new tab" link + instructions

### O3. Kibana Integration
- [ ] If Kibana iframe: dashboards load inside the page
- [ ] If React fallback: charts render using same APIs as dashboard
- [ ] Date range selector on analytics page works
- [ ] "Open in Kibana" button → opens Kibana URL in new tab

### O4. Empty State
- [ ] New user with no data: "Dashboards appear once you have feedback data."

---

## P. Widget → Page Navigation (Cross-links)

Verify ALL clickable elements navigate correctly:
- [ ] Summary card → correct page
- [ ] Volume chart data point → /feedback filtered by date
- [ ] Sentiment donut segment → /feedback?sentiment=X
- [ ] Top issue "Investigate" → agent chat
- [ ] Top issue "Generate Spec" → agent chat
- [ ] Area bar → /feedback?area=X
- [ ] At-risk customer row → /customers/{id}
- [ ] At-risk "View all" → /customers filtered
- [ ] Recent feedback item → feedback detail
- [ ] Source pie slice → /feedback?source=X
- [ ] Segment bar → /feedback?segment=X&area=Y
- [ ] Browser back from any linked page → returns to dashboard

---

## Q. API Verification (curl or devtools)

- [ ] `GET /api/v1/analytics/summary?period=30d` → 200, 4 metrics with trends
- [ ] `GET /api/v1/analytics/volume?period=30d` → 200, time series data
- [ ] `GET /api/v1/analytics/sentiment?period=30d` → 200, breakdown percentages sum to ~100
- [ ] `GET /api/v1/analytics/top-issues?period=30d&limit=5` → 200, ranked list
- [ ] `GET /api/v1/analytics/areas?period=30d` → 200, areas with sentiment
- [ ] `GET /api/v1/analytics/at-risk?period=30d&limit=5` → 200, customer list
- [ ] `GET /api/v1/analytics/sources?period=30d` → 200, source counts
- [ ] `GET /api/v1/analytics/segments?period=30d` → 200, segment comparison
- [ ] `GET /api/v1/user/preferences` → 200, dashboard preferences
- [ ] `PUT /api/v1/user/preferences` with widget toggles → 200, saved
- [ ] All endpoints accept `period` param
- [ ] All endpoints require auth
- [ ] All endpoints isolate by org_id

---

## R. UI/UX Quality

- [ ] Dashboard layout matches the 2-column grid from spec
- [ ] Charts render correctly in dark mode (axis labels, legends visible)
- [ ] Charts render correctly in light mode
- [ ] Chart colors distinguishable (not too similar)
- [ ] Source badge colors on dashboard match feedback page
- [ ] Health score colors consistent everywhere
- [ ] Loading skeletons on every widget
- [ ] No layout shift when widgets load
- [ ] Agent chat bubble still visible
- [ ] Sidebar navigation still works
- [ ] All dashboard pages work in dark + light mode

---

## S. Backend Tests

- [ ] Run: `docker compose exec backend pytest`
- [ ] All Phase 1-6 tests still pass
- [ ] All Phase 7 tests pass:
  - [ ] test_analytics_service.py (11 tests)
  - [ ] test_analytics_routes.py (7 tests)
- [ ] No test failures

---

## T. Frontend Build

- [ ] No TypeScript errors
- [ ] No console errors during dashboard interaction
- [ ] No React warnings

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| Pre-Check (Phases 1-6) | 7 | [ ] |
| A. Summary Cards | 9 | [ ] |
| B. Volume Chart | 9 | [ ] |
| C. Sentiment Donut | 6 | [ ] |
| D. Top Issues | 10 | [ ] |
| E. Area Breakdown | 6 | [ ] |
| F. At-Risk Table | 7 | [ ] |
| G. Recent Feed | 5 | [ ] |
| H. Source Pie | 5 | [ ] |
| I. Segment Chart | 6 | [ ] |
| J. Date Range | 7 | [ ] |
| K. Customization | 6 | [ ] |
| L. Refresh | 3 | [ ] |
| M. Empty State | 4 | [ ] |
| N. Loading States | 4 | [ ] |
| O. Analytics Page | 8 | [ ] |
| P. Cross-links | 12 | [ ] |
| Q. API Verification | 13 | [ ] |
| R. UI/UX Quality | 11 | [ ] |
| S. Backend Tests | 4 | [ ] |
| T. Frontend Build | 3 | [ ] |
| **TOTAL** | **~145** | |

**Phase 7 is DONE when every box above is checked.**
