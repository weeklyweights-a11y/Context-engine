# Phase 4: Search + Feedback Detail + Customer Profiles

> **Goal:** PMs can search feedback semantically, browse with rich filters, see full detail with customer cards and similar items, and view complete customer profiles with feedback history and sentiment trends.
>
> **Done means:** PM types "payment problems" and finds "checkout broken", "credit card declined", "billing confusion". PM clicks a feedback item and sees full detail with customer card. PM clicks a customer and sees their full profile with sentiment trend and feedback history.

---

## Context for the AI Agent

This is Phase 4 of 8. Phases 1-3 are complete — you have auth, ES, product wizard, feedback data, customer data, and ELSER semantic embeddings on feedback.

This phase makes the data useful. Search + browse + filter + detail views. This is the PM's daily workflow for understanding their feedback.

Read `.cursorrules` before starting. Read `UX.md` Flow 4 (Feedback Page) and Flow 5 (Customers Page).

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Semantic search | Hybrid ELSER + keyword search on feedback |
| Feedback page (full) | Search bar, filters, results list, slide-out detail panel |
| Feedback detail | Full text, customer card, similar items, action buttons |
| Customer list (full) | Search, filters, sortable table |
| Customer profile | Full page: metrics, sentiment trend, feedback history |
| Similar feedback | Vector similarity search for "related items" |
| URL-based filter state | Shareable filtered views |

---

## Search API

### POST /api/v1/search/feedback

The primary search endpoint. Hybrid: keyword + semantic via ELSER.

Request:
```json
{
  "query": "payment problems",
  "filters": {
    "product_area": ["checkout", "billing"],
    "source": ["support_ticket", "app_store_review"],
    "sentiment": ["negative"],
    "customer_segment": ["enterprise"],
    "date_from": "2026-01-01",
    "date_to": "2026-02-20",
    "customer_id": null,
    "has_customer": null
  },
  "sort_by": "relevance",
  "page": 1,
  "page_size": 20
}
```

**Search logic:**

If query is provided (non-empty string):
- Use hybrid search combining:
  1. `text_semantic` field for ELSER semantic matching (via semantic query)
  2. `text` field for BM25 keyword matching (via match query)
- Combine using RRF (Reciprocal Rank Fusion) or a simple bool query with should clauses
- Sort by `_score` (relevance) by default

If query is empty:
- Skip search scoring
- Return all items matching filters
- Sort by `created_at` desc (newest first)

**Filters:** All filters are applied as `bool.filter` clauses (no scoring impact):
- product_area: terms query
- source: terms query
- sentiment: terms query
- customer_segment: terms query
- date_from/date_to: range query on created_at
- customer_id: term query
- has_customer: exists query on customer_id

Response:
```json
{
  "data": [...feedback items with _score...],
  "pagination": { "page": 1, "page_size": 20, "total": 47 },
  "query": "payment problems"
}
```

### GET /api/v1/feedback/{id}/similar

Find feedback items similar to a given item using vector similarity.

- Get the source item
- Use ELSER `more_like_this` or semantic search with the source item's text as query
- Exclude the source item from results
- Return top 5 similar items

Response: `{ "data": [...5 similar items...] }`

---

## Feedback Page (Full Implementation)

Replace the Phase 3 basic list with the full feedback page from UX.md Flow 4.

### Layout
Left side (~70%): search + filters + results list
Right side (~30%): detail slide-out panel (hidden until item clicked)

### Search Bar
- Prominent, top of page
- Placeholder: "Search feedback... (e.g., 'payment problems', 'slow dashboard')"
- Debounced (300ms) — calls search API as PM types
- Clear button (X)

### Filters (below search bar)
Row of filter controls:
- **Product area:** multi-select dropdown (populated from product wizard areas)
- **Source:** multi-select dropdown (11 source types with colored dots)
- **Sentiment:** toggle buttons (Positive / Negative / Neutral / All)
- **Segment:** multi-select dropdown (from product wizard segments)
- **Date range:** presets (7d / 30d / 90d) + custom date picker
- **Customer:** search/autocomplete input (searches customer names)
- **Has customer:** toggle (All / Linked / Unlinked)
- **"Clear all filters"** link

### Filter State in URL
All active filters encoded in URL query params:
```
/feedback?q=payment+problems&area=checkout,billing&sentiment=negative&range=30d
```
- PM can share URL, bookmark filtered views
- Filters persist on page refresh
- Use React Router's useSearchParams

### Results List
Each item card:
- Feedback text (first 2 lines, truncated with "...")
- Source badge (colored pill matching source type)
- Sentiment indicator (green/red/gray dot + score)
- Product area tag
- Customer name (clickable → customer profile)
- Date (relative: "2 days ago")
- Click anywhere on card → opens detail slide-out

Top of results:
- Count: "Showing 47 results"
- Sort: Relevance (when searching) / Date (newest) / Sentiment (most negative)

Bottom: Pagination or "Load more" button

### Feedback Detail Slide-Out

Right panel, slides in from right when item clicked.

**Header:**
- Source badge (large)
- Date
- Close button (X)

**Body:**
- Full feedback text (untruncated)
- Sentiment: colored badge + score (e.g., "Negative -0.72")
- Product area tag
- Rating (stars if available)
- Author: name + email
- Ingestion: "Imported via CSV on Feb 10, 2026"

**Customer Card** (if customer linked):
- Company name (clickable → /customers/{id})
- Segment badge
- MRR / ARR
- Health score (colored)
- Account manager
- Renewal date (warning icon if <60 days)

**Similar Feedback:**
- "5 similar items" header
- List of similar items (from /feedback/{id}/similar)
- Each: text preview (1 line), sentiment dot, date
- Clickable → swaps detail panel to that item

**Actions (bottom):**
- "Ask agent" button → placeholder (wires to chat in Phase 5)
- "Generate spec" button → placeholder (wires in Phase 5)
- "Copy text" → copies to clipboard
- "Star" → bookmarks item (store in localStorage for now)

**Behavior:**
- Close: X button, click outside, Escape key
- Responsive: on small screens, goes full-width overlay

---

## Customer List (Full Implementation)

Replace Phase 3 basic list with full customer list from UX.md Flow 5.

### Search
- Search by company name, account manager, industry
- Debounced, calls GET /customers with search param

### Filters
- Segment: multi-select dropdown
- Health score: range slider (0-100)
- Renewal: within 30d / 60d / 90d / All
- Has negative feedback: Yes / No / All
- ARR range: min-max inputs

### Table
Sortable columns:
| Company Name | Segment | MRR | ARR | Health | Feedback Count | Renewal |
- Health: color-coded (green 70+, yellow 40-69, red <40)
- Renewal: warning icon if within 60 days
- Feedback count: number with "X negative" indicator
- Click row → navigate to /customers/{id}

Pagination at bottom.

---

## Customer Profile Page

**New page: `/customers/{id}`**

### Header
- Company name (large)
- Segment badge + Plan name
- Industry tag

### Key Metrics (card row)
| MRR | ARR | Health Score | Total Feedback | Avg Sentiment | Days to Renewal |
- Each metric as a card with value + color coding where appropriate

### Account Details Section
- Account manager
- Employee count
- Created date
- Renewal date (highlighted if <60 days)
- Plan/tier
- External customer ID

### Sentiment Trend Chart
- Line chart: customer's average sentiment score over time (by month or week)
- Overlay: product-wide average for comparison
- Library: recharts or Chart.js

### Feedback History
- All feedback from this customer (query: customer_id filter)
- Same card format as feedback page
- Filter by product area, sentiment, date
- Click → opens feedback detail (could be modal or navigates with back)

### Specs Mentioning Customer
- Placeholder list: "Coming in Phase 6"

### Actions
- "Ask agent about this customer" → placeholder
- "View all feedback" → navigates to /feedback?customer={id}
- "View in Kibana" → placeholder

---

## Updated API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /search/feedback | Yes | Hybrid semantic + keyword search |
| GET | /feedback/{id}/similar | Yes | Find similar feedback items |
| GET | /customers/{id}/feedback | Yes | All feedback for a customer |
| GET | /customers/{id}/sentiment-trend | Yes | Sentiment over time for customer |

### GET /customers/{id}/feedback

Same as GET /feedback but pre-filtered by customer_id. Supports pagination and additional filters.

### GET /customers/{id}/sentiment-trend

Returns aggregated sentiment data over time for one customer.

Response:
```json
{
  "data": {
    "periods": [
      { "date": "2025-12", "avg_sentiment": -0.3, "count": 4 },
      { "date": "2026-01", "avg_sentiment": -0.5, "count": 7 },
      { "date": "2026-02", "avg_sentiment": -0.2, "count": 3 }
    ],
    "product_average": [
      { "date": "2025-12", "avg_sentiment": -0.1 },
      { "date": "2026-01", "avg_sentiment": -0.15 },
      { "date": "2026-02", "avg_sentiment": -0.12 }
    ]
  }
}
```

Use ES date_histogram aggregation with avg aggregation on sentiment_score.

---

## Services (Backend)

### services/search_service.py
- `search_feedback(org_id, query, filters, sort_by, page, page_size)` — Build and execute hybrid search query
- `find_similar(org_id, feedback_id, size)` — Vector similarity search
- `build_hybrid_query(query, filters)` — Construct ES query with ELSER + BM25 + filters
- `build_filter_clauses(filters)` — Convert filter dict to ES bool filter array

### services/customer_service.py (additions)
- `get_customer_feedback(org_id, customer_id, page, page_size, filters)` — Feedback filtered by customer
- `get_customer_sentiment_trend(org_id, customer_id)` — Date histogram aggregation

---

## Frontend Components

### New/Updated
- `FeedbackPage.tsx` — Full rewrite with search, filters, results, detail panel
- `FeedbackDetailPanel.tsx` — Slide-out detail with customer card + similar
- `FeedbackCard.tsx` — Reusable card for list items
- `CustomerCard.tsx` — Small customer card for detail panel
- `SearchBar.tsx` — Debounced search input
- `FilterBar.tsx` — All filter controls in a row
- `SentimentBadge.tsx` — Colored sentiment indicator
- `SourceBadge.tsx` — Colored source type pill
- `CustomersPage.tsx` — Full rewrite with search, filters, table
- `CustomerProfilePage.tsx` — New page at /customers/{id}
- `SentimentTrendChart.tsx` — Line chart component

### Router Updates
- `/customers/:id` → CustomerProfilePage (protected)

---

## Testing

### test_search_service.py
1. Search with query returns relevant results (semantic match).
2. Search with query "payment" finds "checkout broken" (semantic, not just keyword).
3. Search with empty query returns all items sorted by date.
4. Search with product_area filter → only matching area.
5. Search with sentiment filter → only matching sentiment.
6. Search with date range → only items in range.
7. Search with multiple filters → AND logic.
8. Search results paginated correctly.
9. Search isolates by org_id.

### test_similar.py
1. Find similar for a checkout feedback → returns other checkout items.
2. Find similar excludes the source item.
3. Find similar returns max 5 items.
4. Find similar for org_id isolation.

### test_customer_profile.py
1. Get customer feedback returns only that customer's items.
2. Get customer sentiment trend returns aggregated data.
3. Sentiment trend includes product average overlay.
4. Customer endpoints isolate by org_id.

### test_search_routes.py
1. POST /search/feedback with query → 200 with results.
2. POST /search/feedback with filters → filtered results.
3. POST /search/feedback without auth → 401.
4. GET /feedback/{id}/similar → returns similar items.
5. GET /customers/{id}/feedback → returns customer's feedback.
6. GET /customers/{id}/sentiment-trend → returns trend data.

---

## Non-Negotiable Rules

1. **Hybrid search always.** Never just keyword OR just semantic. Always combine both.
2. **Filters are bool.filter.** They don't affect scoring.
3. **Filter state in URL.** PM must be able to share/bookmark filtered views.
4. **org_id on every search query.** Multi-tenant isolation.
5. **Debounced search.** Never fire on every keystroke.
6. **Detail panel doesn't navigate away.** Slide-out, not a new page (except customer profile).
7. **Customer profile is a full page.** Not a slide-out.

---

## What NOT to Build

- Agent tools or chat (Phase 5)
- Spec generation (Phase 6)
- Dashboard widgets (Phase 7)
- Kibana dashboards (Phase 7)
- Slack connector (Phase 8)

---

## Acceptance Criteria

- [ ] PM can type a query and get semantically relevant results
- [ ] "payment problems" finds "checkout broken", "credit card declined" (semantic match)
- [ ] Empty search returns all items sorted by newest
- [ ] Product area filter works
- [ ] Source type filter works
- [ ] Sentiment filter works
- [ ] Segment filter works
- [ ] Date range filter works
- [ ] Multiple filters combine with AND
- [ ] Filter state reflected in URL (shareable)
- [ ] Search results show count, pagination
- [ ] Click feedback item → detail slide-out opens
- [ ] Detail shows full text, sentiment, source, customer card
- [ ] Similar feedback section shows related items
- [ ] Click customer name → navigates to customer profile
- [ ] Customer list shows search + filters + sortable table
- [ ] Customer profile shows key metrics, account details
- [ ] Customer profile shows sentiment trend chart
- [ ] Customer profile shows feedback history
- [ ] "View all feedback" from customer → feedback page filtered
- [ ] All search/data filtered by org_id
- [ ] All backend tests pass
- [ ] All previous phase tests still pass

---

## How to Give This to Cursor

> Read docs/PHASE_4_SPEC.md, PROJECT.md, and UX.md (Flow 4, Flow 5). This is the spec for Phase 4. The .cursorrules file applies. Do NOT start building yet. Create implementation plan, wait for approval.

---

## After Phase 4

Phase 5: Agent + Tools. ES Agent Builder with 7 tools, functional chat panel, conversation history.
