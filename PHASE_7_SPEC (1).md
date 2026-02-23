# Phase 7: Dashboard + Analytics + Kibana

> **Goal:** The dashboard becomes the PM's command center with 9 real widgets. Kibana dashboards embed for deep analytics. Every chart is clickable, linking to feedback or customer pages.
>
> **Done means:** PM opens dashboard and sees real data: summary cards with trends, volume chart, sentiment donut, top issues, at-risk customers, recent feedback. PM clicks "Analytics" and sees embedded Kibana dashboards. Every widget links to detailed views.

---

## Context for the AI Agent

This is Phase 7 of 8. Phases 1-6 complete — full pipeline from ingestion to spec generation.

This phase makes everything visible at a glance. The dashboard is what PMs check every morning. Kibana gives power users deep analytics.

Read `.cursorrules`. Read `UX.md` Flow 3 (Dashboard) and Flow 7 (Analytics Page).

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| 9 dashboard widgets | Real-time metrics, charts, tables powered by ES aggregations |
| Dashboard customization | Show/hide widgets, saved per user |
| Date range selector | Applies to all widgets |
| Analytics page | Kibana dashboards embedded via iframe |
| Widget → page navigation | Click chart segment → filtered feedback/customer page |
| ES|QL aggregation endpoints | Backend APIs powering each widget |

---

## Dashboard Widgets

### Widget 1: Summary Cards (top row, 4 cards)

| Card | Value | Trend |
|------|-------|-------|
| Total Feedback | Count for period | ↑12% vs previous period |
| Avg Sentiment | Score (-1 to 1) | ↓5% vs previous period |
| Active Issues | Count of negative clusters | ↑ or ↓ vs previous |
| At-Risk Customers | Customers with health <40 or negative trend | Count |

Each card: clickable → navigates to relevant page.

**API: GET /api/v1/analytics/summary?period=30d**

ES queries:
- Total feedback: count with date filter
- Previous period count for trend calculation
- Avg sentiment: avg aggregation on sentiment_score
- Active issues: count of distinct product_areas with avg_sentiment < -0.3
- At-risk: count of customers with health_score < 40

### Widget 2: Feedback Volume Over Time (line chart)

- X axis: dates. Y axis: feedback count.
- Toggle lines per product area.
- Hover: show daily count.
- Click data point → /feedback?date={date}

**API: GET /api/v1/analytics/volume?period=30d&areas=checkout,billing**

ES: date_histogram aggregation, optional terms sub-aggregation on product_area.

### Widget 3: Sentiment Breakdown (donut chart)

- 3 segments: Positive % / Negative % / Neutral %
- Click segment → /feedback?sentiment={type}

**API: GET /api/v1/analytics/sentiment?period=30d**

ES: terms aggregation on sentiment field with value_count.

### Widget 4: Top Issues (ranked cards)

Top 3-5 issues showing:
- Issue name (product_area + key theme)
- Feedback count + growth rate
- Severity badge: Critical / Emerging / Stable / Improving
- Affected customers + total ARR
- "Investigate" → opens agent chat
- "Generate Spec" → opens agent chat

**API: GET /api/v1/analytics/top-issues?period=30d&limit=5**

Reuse logic from agent top_issues tool (Phase 5).

### Widget 5: Product Area Breakdown (horizontal bar chart)

- One bar per product area
- Bar length = feedback count
- Color = avg sentiment (green → yellow → red gradient)
- Click bar → /feedback?area={area}

**API: GET /api/v1/analytics/areas?period=30d**

ES: terms aggregation on product_area with avg sub-aggregation on sentiment_score.

### Widget 6: At-Risk Customers (table)

| Company | ARR | Negative Feedback (30d) | Renewal | Health |
- Sorted by risk (lowest health first)
- Warning icon on renewal <60 days
- Health: green/yellow/red
- Click row → /customers/{id}
- Max 5 rows, "View all" link → /customers?health_max=40

**API: GET /api/v1/analytics/at-risk?period=30d&limit=5**

ES: search customers with health_score <50 OR significant negative feedback, sorted by health asc.

### Widget 7: Recent Feedback Stream

- Latest 10 items
- Each: text preview, source badge, sentiment dot, area tag, time ago
- Click → opens feedback detail (could navigate to /feedback?id={id})
- Auto-refreshes every 30 seconds (or manual refresh)

**API: GET /api/v1/feedback?sort_by=date&sort_order=desc&page_size=10**

Already exists from Phase 3/4.

### Widget 8: Source Distribution (pie chart)

- Slices per source type
- Hover: count + percentage
- Click slice → /feedback?source={type}

**API: GET /api/v1/analytics/sources?period=30d**

ES: terms aggregation on source field.

### Widget 9: Feedback by Segment (grouped bar chart)

- Groups: product areas (or overall)
- Bars per segment: enterprise / SMB / consumer / trial
- Helps PM see which segment hurts most per area
- Click bar → /feedback?segment={seg}&area={area}

**API: GET /api/v1/analytics/segments?period=30d**

ES: terms aggregation on customer_segment, optionally with product_area sub-aggregation.

---

## Dashboard Top Bar

- **Date range selector:** 7d / 30d / 90d / Custom (date picker)
  - Applies to ALL widgets simultaneously
  - Stored in URL query param: /dashboard?period=30d
- **"Customize Dashboard"** button: dropdown with checkboxes for each widget
  - Preferences saved via PUT /api/v1/user/preferences
- **Refresh button:** re-fetches all widget data

---

## Dashboard Customization

Users can show/hide widgets. Preferences stored in the users index.

Add field to users index:
| Field | ES Type |
|-------|---------|
| dashboard_preferences | object |

```json
{
  "dashboard_preferences": {
    "visible_widgets": ["summary", "volume", "sentiment", "top_issues", "areas", "at_risk", "recent", "sources", "segments"],
    "default_period": "30d"
  }
}
```

**API:**
- GET /api/v1/user/preferences — get current preferences
- PUT /api/v1/user/preferences — save preferences

---

## Analytics API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /analytics/summary | Yes | 4 summary card metrics |
| GET | /analytics/volume | Yes | Feedback count over time |
| GET | /analytics/sentiment | Yes | Sentiment breakdown |
| GET | /analytics/top-issues | Yes | Ranked issues |
| GET | /analytics/areas | Yes | Product area breakdown |
| GET | /analytics/at-risk | Yes | At-risk customers |
| GET | /analytics/sources | Yes | Source distribution |
| GET | /analytics/segments | Yes | Feedback by segment |
| GET | /user/preferences | Yes | Dashboard preferences |
| PUT | /user/preferences | Yes | Save preferences |

All accept `period` query param (7d / 30d / 90d / custom with from/to).

---

## Analytics Page (Kibana Embedded)

### AnalyticsPage.tsx

4 sub-tabs:

**Tab 1: Feedback Overview**
- Kibana dashboard embedded via iframe
- Dashboard includes: volume chart, source pie, area bars, sentiment donut
- Or: if Kibana iframe setup is complex, show our own charts using same APIs as dashboard

**Tab 2: Trends & Alerts**
- Sentiment by area over time
- Week-over-week comparison
- Growing issues highlight

**Tab 3: Deep Dive**
- Fully filterable Kibana dashboard
- Individual feedback items visible

**Tab 4: Custom**
- "Open Kibana in new tab" link
- Instructions for creating custom dashboards

Top bar: date range + "Open in Kibana" button (opens Kibana URL from settings)

**Kibana iframe approach:**
```html
<iframe src="{KIBANA_URL}/app/dashboards#/view/{dashboard_id}?embed=true&_g=(time:(from:now-30d,to:now))" />
```

If Kibana iframe embedding has CORS/auth issues, fall back to:
- Build the same dashboards in React using recharts
- Include "Open in Kibana" link for full access

---

## Services (Backend)

### services/analytics_service.py
- `get_summary(org_id, period)` — 4 card metrics with trends
- `get_volume(org_id, period, areas)` — Date histogram
- `get_sentiment_breakdown(org_id, period)` — Sentiment terms agg
- `get_top_issues(org_id, period, limit)` — Reuse from agent tools
- `get_area_breakdown(org_id, period)` — Terms agg with sentiment
- `get_at_risk_customers(org_id, period, limit)` — Customer query
- `get_source_distribution(org_id, period)` — Source terms agg
- `get_segment_breakdown(org_id, period)` — Segment agg
- `calculate_trend(current, previous)` — % change calculation

### services/user_service.py (additions)
- `get_preferences(user_id)` — Get dashboard preferences
- `update_preferences(user_id, preferences)` — Save preferences

---

## Frontend

### DashboardPage.tsx (Full Rewrite)

Replace empty state with full dashboard.

Layout:
```
┌─────────────────────────────────────────┐
│ Date Range: [7d] [30d] [90d] [Custom]  │ [Customize] [↻]
├────────┬────────┬────────┬──────────────┤
│ Total  │  Avg   │ Active │   At-Risk    │ ← Widget 1: Summary Cards
│ 847 ↑  │ -0.23 ↓│ 4 Crit │  3 accounts  │
├────────┴────────┴────────┴──────────────┤
│ Widget 2: Volume Chart    │ Widget 3:    │
│ [line chart]              │ [donut]      │
├───────────────────────────┤──────────────┤
│ Widget 4: Top Issues      │ Widget 5:    │
│ [ranked cards]            │ [bar chart]  │
├───────────────────────────┤──────────────┤
│ Widget 6: At-Risk Table   │ Widget 7:    │
│ [table]                   │ [feed]       │
├───────────────────────────┤──────────────┤
│ Widget 8: Source Pie      │ Widget 9:    │
│ [pie chart]               │ [grouped bar]│
└───────────────────────────┴──────────────┘
```

Each widget:
- Loading skeleton while data fetches
- Error state if API fails
- "No data" state if empty
- Clickable elements navigate to relevant pages

### Chart Library

Use **recharts** (already available in React artifacts). Components needed:
- LineChart (volume)
- PieChart (sentiment donut, sources)
- BarChart (areas horizontal, segments grouped)

### Widget Components
- `SummaryCards.tsx`
- `VolumeChart.tsx`
- `SentimentDonut.tsx`
- `TopIssuesWidget.tsx`
- `AreaBreakdown.tsx`
- `AtRiskTable.tsx`
- `RecentFeedback.tsx`
- `SourceDistribution.tsx`
- `SegmentBreakdown.tsx`
- `CustomizeDashboard.tsx` — dropdown with checkboxes

### AnalyticsPage.tsx
- 4-tab layout
- Kibana iframe or React chart fallback
- Date range selector
- "Open in Kibana" button

---

## Kibana Dashboard Setup

Create a setup script/guide for configuring Kibana dashboards:

### Pre-built dashboards to create in Kibana:

**Dashboard 1: Feedback Overview**
- Lens: feedback count over time
- Lens: source distribution pie
- Lens: product area bar chart
- Lens: sentiment donut

**Dashboard 2: Trends & Alerts**
- Lens: sentiment by area over time (line per area)
- Lens: week-over-week volume comparison
- Lens: top growing areas table

**Dashboard 3: Deep Dive**
- ES|QL table: all feedback items with filters
- Lens: individual feedback with full text

Store dashboard IDs in settings for iframe embedding.

---

## Testing

### test_analytics_service.py
1. Summary returns 4 metrics with trend calculations.
2. Volume returns date histogram data.
3. Sentiment returns breakdown percentages (sum to 100).
4. Top issues returns ranked list with scores.
5. Area breakdown returns areas with sentiment.
6. At-risk returns customers sorted by health.
7. Sources returns distribution.
8. Segments returns comparison data.
9. All filtered by org_id.
10. Empty data returns zeros, not errors.
11. Trend calculation: 100 → 120 = +20%.

### test_analytics_routes.py
1. GET /analytics/summary → 200 with 4 metrics.
2. GET /analytics/volume → 200 with time series.
3. All analytics endpoints accept period param.
4. All require auth.
5. All isolate by org_id.
6. GET /user/preferences → 200.
7. PUT /user/preferences → saved and returned.

---

## Non-Negotiable Rules

1. **Every widget powered by real ES data.** No mocked numbers.
2. **Date range applies globally.** All widgets respect the selected period.
3. **Every chart element clickable.** Links to filtered pages.
4. **Loading skeletons on all widgets.** No layout shift.
5. **org_id on every aggregation query.**
6. **Graceful empty states.** Dashboard works with 0 data, 1 item, or 10,000.

---

## What NOT to Build

- Slack connector (Phase 8)
- PDF export for specs (Phase 8)
- Full responsive optimization (Phase 8)

---

## Acceptance Criteria

- [ ] Dashboard shows 9 widgets with real data
- [ ] Summary cards show metrics with trend arrows
- [ ] Volume chart shows feedback over time with area toggle
- [ ] Sentiment donut shows breakdown, clickable segments
- [ ] Top issues ranked with feedback count, ARR, severity badges
- [ ] Top issues "Investigate" opens agent chat
- [ ] Top issues "Generate Spec" opens agent chat
- [ ] Product area bars show count + sentiment coloring
- [ ] At-risk table shows customers sorted by health
- [ ] Recent feed shows latest 10 items
- [ ] Source pie shows distribution
- [ ] Segment chart shows comparison
- [ ] Date range selector applies to all widgets (7d/30d/90d/custom)
- [ ] "Customize Dashboard" shows/hides widgets
- [ ] Widget preferences persist on reload
- [ ] Clicking chart elements navigates to filtered pages
- [ ] Analytics page shows Kibana iframe or React charts
- [ ] "Open in Kibana" link works
- [ ] Dashboard works with empty data (no crashes)
- [ ] All backend tests pass
- [ ] All previous phase tests still pass

---

## How to Give This to Cursor

> Read docs/PHASE_7_SPEC.md, PROJECT.md, and UX.md (Flow 3, Flow 7). This is Phase 7. Create implementation plan, wait for approval.

---

## After Phase 7

Phase 8: Polish + Ship. Settings complete, Slack connector, responsive, README, demo.
