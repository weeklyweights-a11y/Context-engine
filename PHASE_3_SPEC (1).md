# Phase 3: Data Ingestion (Feedback + Customers)

> **Goal:** PMs can get real data into the system. Upload feedback via CSV or manual entry. Upload customer profiles via CSV or manual entry. Feedback gets ELSER embeddings for semantic search. Product areas auto-detected from feedback text.
>
> **Done means:** PM uploads a feedback CSV, maps columns, sees items in the feedback list. PM adds feedback manually. PM uploads customers CSV. PM adds customers manually. All data lands in Elasticsearch with correct fields. Feedback has semantic embeddings. Settings > Data Upload shows upload history.

---

## Context for the AI Agent

This is Phase 3 of 8. Phases 1-2 are complete — you have auth, ES connection, sidebar, empty pages, product wizard, and product context in ES.

In this phase you are building the data ingestion layer. This is where ALL feedback and customer data enters the system. Every future feature (search, agent, specs, dashboard) depends on this data existing in ES with the right shape.

Read `.cursorrules` before starting. Read `UX.md` Section B (Upload Feedback), Section C (Upload Customers), and Flow 8 (Settings > Data Upload).

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Feedback CSV upload | PM uploads CSV, maps columns, preview, import into ES |
| Feedback manual entry | PM fills form, single item into ES |
| Customer CSV upload | PM uploads CSV, maps columns, import into ES |
| Customer manual entry | PM fills form, single profile into ES |
| {org_id}-feedback index | With ELSER semantic_text field for future semantic search |
| {org_id}-customers index | Customer profiles linked to segments |
| Upload history | Track all imports in Settings > Data Upload |
| Auto-detect product areas | After feedback upload, suggest product areas from text |

---

## Elasticsearch Indexes

### Index: `{org_id}-feedback`

Created on first feedback upload. This is the core index of the entire system.

| Field | ES Type | Purpose |
|-------|---------|---------|
| id | keyword | UUID |
| org_id | keyword | Multi-tenancy |
| text | text | Raw feedback text (keyword search) |
| text_semantic | semantic_text (ELSER) | Same text, ELSER embeddings (semantic search) |
| source | keyword | One of 11 source types |
| sentiment | keyword | positive / negative / neutral |
| sentiment_score | float | -1.0 to 1.0 |
| rating | integer | 1-5 if available |
| product_area | keyword | Linked product area name |
| customer_id | keyword | Linked to customers index |
| customer_name | keyword | Denormalized for display |
| customer_segment | keyword | Denormalized for filtering |
| author_name | keyword | Person who gave feedback |
| author_email | keyword | Their email |
| tags | keyword (array) | Auto-detected or manual |
| source_file | keyword | Original filename if from CSV |
| ingestion_method | keyword | csv_upload / manual_entry / slack_connector |
| created_at | date | When feedback was originally created |
| ingested_at | date | When we imported it |
| metadata | object (dynamic) | Source-specific extra data |

**ELSER Setup:** The `text_semantic` field uses `semantic_text` field type which automatically generates ELSER embeddings. This requires an ELSER inference endpoint to be deployed on the Elastic Cloud cluster.

**Before creating the index, check/deploy ELSER:**
1. Check if `.elser_model_2_linux-x86_64` is deployed: `GET /_ml/trained_models/.elser_model_2_linux-x86_64/_stats`
2. If not deployed, create inference endpoint: `PUT /_inference/sparse_embedding/elser-endpoint` with model_id `.elser_model_2_linux-x86_64`
3. The `text_semantic` field mapping references this inference endpoint.

### Index: `{org_id}-customers`

| Field | ES Type | Purpose |
|-------|---------|---------|
| id | keyword | UUID |
| org_id | keyword | Multi-tenancy |
| company_name | text + keyword | Company name |
| customer_id_external | keyword | PM's own customer ID (from CSV) |
| segment | keyword | Maps to product wizard segments |
| plan | keyword | Pricing tier name |
| mrr | float | Monthly recurring revenue |
| arr | float | Annual recurring revenue |
| account_manager | keyword | Owner |
| renewal_date | date | Contract renewal |
| health_score | integer | 0-100 |
| industry | keyword | Company industry |
| employee_count | integer | Company size |
| created_at | date | When customer was added |
| updated_at | date | Last modified |
| metadata | object (dynamic) | Extra fields from CSV |

### Index: `upload-history`

Single shared index (not per-org, but filtered by org_id).

| Field | ES Type | Purpose |
|-------|---------|---------|
| id | keyword | UUID |
| org_id | keyword | Multi-tenancy |
| upload_type | keyword | feedback / customers |
| filename | keyword | Original file name |
| total_rows | integer | Rows in file |
| imported_rows | integer | Successfully imported |
| failed_rows | integer | Failed to parse |
| status | keyword | pending / processing / completed / failed |
| column_mapping | object | Saved column mapping |
| error_message | text | If failed |
| created_at | date | When upload started |
| completed_at | date | When finished |

---

## Feedback CSV Upload Flow

### Step 1: Upload File

**Endpoint: `POST /api/v1/feedback/upload-csv`**

- Accepts multipart file upload
- Validate: .csv extension, max 50MB
- Read file, detect columns (headers), count rows
- Return: detected columns + suggested mapping + total rows + upload_id

### Step 2: Column Mapping

**Endpoint: `POST /api/v1/feedback/upload-csv/{upload_id}/confirm`**

Frontend shows column mapping UI:
- Left column: our fields (text, source, product_area, customer, date, sentiment, rating)
- Right column: dropdown of CSV columns
- "text" column is required — if not mapped, block import
- Auto-detect: match CSV headers using keyword matching (case-insensitive):

| Our Field | CSV Headers to Match |
|-----------|---------------------|
| text | feedback, message, text, description, content, body, comment, note, review, request |
| source | source, source_type, channel, origin, type |
| product_area | area, product_area, module, feature, category, topic |
| customer_name | company, customer, organization, org, account, company_name |
| author_name | name, author, user, reviewer, submitter |
| author_email | email, customer_email, user_email, contact_email |
| date | date, created, created_at, timestamp, time, submitted |
| sentiment | sentiment, tone, feeling |
| rating | rating, score, stars, nps |

- Show preview: first 5 rows mapped to our fields
- PM confirms or adjusts mapping
- PM selects: source type (dropdown of 11 types) if not in CSV, "Auto-detect" for product area and sentiment

### Step 3: Import

**Endpoint: `POST /api/v1/feedback/upload-csv/{upload_id}/import`**

- Read CSV using confirmed column mapping
- For each row: parse, validate, create feedback item
- Use ES Bulk API (batch 500 rows per bulk call)
- Track progress in upload-history
- Skip bad rows (increment failed_rows, continue)
- After import: run auto-detection for product areas if requested

**Sentiment analysis:** For now, use a simple keyword-based approach (not LLM):
- Positive keywords: great, love, excellent, amazing, helpful, easy, fast, works well
- Negative keywords: broken, terrible, hate, slow, confusing, frustrated, bug, crash, error, issue
- Score: count positive vs negative keywords, normalize to -1.0 to 1.0
- This is a placeholder — Phase 5 agent can re-analyze with better logic

**Product area auto-detection:** After import, if PM selected "Auto-detect":
- Get existing product areas from product wizard
- For each area, count how many feedback items mention it (keyword match on area name)
- Also detect NEW potential areas: find most frequent nouns/bigrams not already in areas list
- Return suggested areas to frontend for PM to confirm

### Step 4: Results

Return import summary:
```json
{
  "data": {
    "upload_id": "...",
    "total_rows": 800,
    "imported_rows": 792,
    "failed_rows": 8,
    "detected_areas": [
      { "name": "checkout", "count": 102, "is_new": true },
      { "name": "dashboard", "count": 61, "is_new": false }
    ]
  }
}
```

---

## Feedback Manual Entry

**Endpoint: `POST /api/v1/feedback/manual`**

Request:
```json
{
  "text": "The checkout flow is confusing. I got stuck at payment.",
  "source": "support_ticket",
  "product_area": "checkout",
  "customer_id": "cust_042",
  "author_name": "John Smith",
  "author_email": "john@techflow.com",
  "rating": 2,
  "created_at": "2026-02-10"
}
```

- `text` is required. Everything else optional.
- Auto-analyze sentiment (same keyword approach)
- If customer_id provided, look up customer for denormalized fields
- Index into `{org_id}-feedback`
- Return created item

---

## Customer CSV Upload Flow

Same pattern as feedback CSV:

1. Upload file → detect columns → return mapping
2. Confirm mapping with preview
3. Import via Bulk API

Column auto-detection:

| Our Field | CSV Headers to Match |
|-----------|---------------------|
| company_name | company, company_name, customer, organization, org, account, name |
| customer_id_external | id, customer_id, account_id, external_id |
| segment | segment, tier, type, plan_type, customer_type |
| plan | plan, plan_name, subscription, product |
| mrr | mrr, monthly_revenue, monthly |
| arr | arr, annual_revenue, annual, revenue |
| account_manager | manager, account_manager, owner, csm, am |
| renewal_date | renewal, renewal_date, contract_end, expiry |
| health_score | health, health_score, score, nps |
| industry | industry, vertical, sector |
| employee_count | employees, employee_count, company_size, size |

**Endpoints:**
- POST /api/v1/customers/upload-csv → returns mapping
- POST /api/v1/customers/upload-csv/{upload_id}/confirm → confirm mapping
- POST /api/v1/customers/upload-csv/{upload_id}/import → import

---

## Customer Manual Entry

**Endpoint: `POST /api/v1/customers/manual`**

Request:
```json
{
  "company_name": "TechFlow Inc",
  "segment": "enterprise",
  "plan": "Enterprise Pro",
  "mrr": 2500,
  "arr": 30000,
  "account_manager": "Sarah Chen",
  "renewal_date": "2026-04-15",
  "health_score": 72,
  "industry": "fintech",
  "employee_count": 450
}
```

- `company_name` is required. Everything else optional.
- If segment doesn't match wizard segments, store as-is (don't error).

---

## API Endpoints Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /feedback/upload-csv | Yes | Upload CSV, get column mapping |
| POST | /feedback/upload-csv/{id}/confirm | Yes | Confirm column mapping |
| POST | /feedback/upload-csv/{id}/import | Yes | Run import |
| POST | /feedback/manual | Yes | Add single feedback item |
| GET | /feedback | Yes | List feedback (paginated, filtered by source_type) |
| GET | /feedback/{id} | Yes | Single feedback item |
| GET | /feedback/count | Yes | Total feedback count for org |
| POST | /customers/upload-csv | Yes | Upload CSV, get column mapping |
| POST | /customers/upload-csv/{id}/confirm | Yes | Confirm mapping |
| POST | /customers/upload-csv/{id}/import | Yes | Run import |
| POST | /customers/manual | Yes | Add single customer |
| GET | /customers | Yes | List customers (paginated) |
| GET | /customers/{id} | Yes | Single customer profile |
| GET | /customers/count | Yes | Total customer count for org |
| GET | /uploads | Yes | Upload history for org |
| GET | /uploads/{id} | Yes | Single upload status |

### GET /feedback

Query params: page (default 1), page_size (default 20), source_type (filter), product_area (filter), sentiment (filter), sort_by (date/sentiment), sort_order (asc/desc)

Returns paginated list with standard response shape.

### GET /customers

Query params: page, page_size, segment (filter), health_min, health_max, sort_by, sort_order

---

## Services (Backend)

### services/feedback_service.py
- `create_feedback_item(org_id, data)` — Create single item, auto-analyze sentiment
- `create_feedback_items_bulk(org_id, items)` — Bulk create via ES Bulk API
- `get_feedback_items(org_id, page, page_size, filters)` — Paginated list with filters
- `get_feedback_item(org_id, item_id)` — Single item
- `get_feedback_count(org_id)` — Total count
- `analyze_sentiment(text)` — Keyword-based sentiment analysis

### services/customer_service.py
- `create_customer(org_id, data)` — Create single customer
- `create_customers_bulk(org_id, customers)` — Bulk create
- `get_customers(org_id, page, page_size, filters)` — Paginated list
- `get_customer(org_id, customer_id)` — Single customer
- `get_customer_count(org_id)` — Total count

### services/csv_service.py
- `detect_feedback_columns(headers)` — Auto-map CSV headers to feedback fields
- `detect_customer_columns(headers)` — Auto-map CSV headers to customer fields
- `parse_csv_file(file, column_mapping)` — Parse CSV into list of dicts
- `validate_row(row, required_fields)` — Validate single row

### services/upload_service.py
- `create_upload(org_id, upload_type, filename, total_rows)` — Create upload history record
- `update_upload(upload_id, status, imported_rows, failed_rows)` — Update progress
- `get_uploads(org_id)` — List uploads for org
- `get_upload(org_id, upload_id)` — Single upload

### services/area_detection_service.py
- `detect_areas(org_id, feedback_texts)` — Analyze texts, return suggested product areas
- `match_existing_areas(texts, existing_areas)` — Count mentions of existing areas
- `find_new_areas(texts, existing_areas)` — Find frequent terms not in existing areas

---

## Frontend

### Upload Feedback (component, used in onboarding + settings)

**FeedbackUpload.tsx**

Tab 1: CSV Upload
- Drag-and-drop zone with file icon
- After file selected: show filename + size + "Upload" button
- After upload: Column Mapping screen
  - Each field row: Our field (left) → dropdown of CSV columns (right)
  - Auto-detected mappings pre-selected
  - Required: text field must be mapped
  - Source type dropdown (if not in CSV)
  - "Auto-detect product areas" checkbox
  - "Auto-analyze sentiment" checkbox
  - Preview table: first 5 rows
  - "Import X items" button
- During import: progress bar
- After import: success summary with detected areas (confirm/reject UI)

Tab 2: Manual Entry
- Textarea for feedback text (required)
- Source dropdown (11 options)
- Product area dropdown (from wizard + "Other")
- Customer search (autocomplete from existing customers)
- Author name, email (text inputs)
- Date picker (default today)
- Rating (1-5 star selector)
- "Add Feedback" button
- "Add another" checkbox

### Upload Customers (component)

**CustomerUpload.tsx**

Same pattern as FeedbackUpload but for customer fields.

### Feedback List Page Update

**FeedbackPage.tsx** — Replace empty state with:
- Table/list of feedback items
- Each row: text (truncated), source badge (colored), sentiment dot, product area, customer name, date
- Pagination controls
- Filter: source type dropdown
- If no items: show empty state with upload CTA

### Customers List Page Update

**CustomersPage.tsx** — Replace empty state with:
- Table of customers
- Each row: company name, segment badge, MRR, ARR, health (colored), feedback count, renewal date
- Pagination controls
- If no items: show empty state with upload CTA

### Settings > Data Upload Tab

Replace placeholder with:
- Two sections: "Upload Feedback" and "Upload Customers" (use same components)
- Upload History table below: Date, Type, Filename, Items Imported, Status badge

### Onboarding Updates

Update onboarding flow:
- Section B (Upload Feedback) now functional — uses FeedbackUpload component
- Section C (Upload Customers) now functional — uses CustomerUpload component
- Progress: Product ✅ → Feedback (active) → Customers

---

## ELSER Deployment

Before creating the feedback index, the backend must ensure ELSER is ready:

```python
def ensure_elser_deployed(es_client):
    """Check if ELSER inference endpoint exists, create if not."""
    try:
        es_client.inference.get(inference_id="elser-endpoint")
    except NotFoundError:
        es_client.inference.put(
            inference_id="elser-endpoint",
            body={
                "service": "elser",
                "service_settings": {
                    "num_allocations": 1,
                    "num_threads": 1
                }
            }
        )
        # Wait for model to be ready (can take a few minutes on first deploy)
```

The feedback index mapping uses:
```json
{
  "text_semantic": {
    "type": "semantic_text",
    "inference_id": "elser-endpoint"
  }
}
```

---

## Testing

### test_feedback_service.py
1. Create feedback item → stored in ES with correct fields.
2. Create feedback with auto-sentiment → sentiment field populated.
3. Bulk create 100 items → all stored, no duplicates.
4. List feedback paginated → correct page_size and total.
5. List feedback filtered by source → only matching items.
6. List feedback filtered by product_area → only matching.
7. Get single feedback item → correct fields.
8. Get feedback for wrong org → not found (multi-tenant).
9. Feedback count returns correct number.

### test_customer_service.py
1. Create customer → stored with correct fields.
2. Bulk create customers → all stored.
3. List customers paginated.
4. List customers filtered by segment.
5. Get single customer.
6. Customer for wrong org → not found.
7. Customer count correct.

### test_csv_service.py
1. Detect feedback columns matches known headers.
2. Detect feedback columns case-insensitive.
3. Detect feedback columns with unknown headers → partial mapping.
4. Detect customer columns matches known headers.
5. Parse CSV row with full mapping → correct dict.
6. Parse CSV row with partial mapping → missing fields are None.
7. Validate row with missing required field → error.

### test_feedback_routes.py
1. POST /feedback/upload-csv with valid CSV → returns mapping.
2. POST /feedback/upload-csv with non-CSV → 400.
3. POST /feedback/upload-csv/{id}/import → items appear in GET /feedback.
4. POST /feedback/manual with text → 200, item created.
5. POST /feedback/manual without text → 422.
6. GET /feedback returns paginated list.
7. GET /feedback with source_type filter works.
8. GET /feedback/{id} returns item.
9. GET /feedback/{id} wrong org → 404.

### test_customer_routes.py
1. POST /customers/upload-csv with valid CSV → returns mapping.
2. POST /customers/manual with company_name → 200.
3. POST /customers/manual without company_name → 422.
4. GET /customers returns paginated list.
5. GET /customers/{id} returns customer.
6. GET /customers/{id} wrong org → 404.

### test_upload_service.py
1. Create upload → status pending.
2. Update upload → status + counts updated.
3. List uploads for org → only this org's uploads.

### test_sentiment.py
1. Positive text → positive sentiment + positive score.
2. Negative text → negative sentiment + negative score.
3. Neutral text → neutral sentiment + ~0 score.

---

## Non-Negotiable Rules

Everything from previous phases still applies, plus:

1. **ES Bulk API for CSV imports.** Never loop individual index calls for 10+ items.
2. **ELSER semantic_text on feedback.** Must be there from day one, even if search isn't built yet.
3. **Failed rows don't kill imports.** Skip bad rows, continue, report count.
4. **Column mapping is a 2-step flow.** Upload → mapping → import. Not one step.
5. **org_id on every document.** Multi-tenant isolation on every query.
6. **Upload history tracked.** PM can see what they've imported.
7. **Sentiment is keyword-based for now.** Good enough placeholder. Agent improves it later.
8. **Reuse components.** Same upload components in onboarding AND settings.

---

## What NOT to Build

- Semantic search (Phase 4)
- Feedback detail slide-out (Phase 4)
- Customer profile page (Phase 4)
- Agent tools or chat (Phase 5)
- Spec generation (Phase 6)
- Dashboard widgets (Phase 7)
- Slack connector (Phase 8)
- LLM-based sentiment (future)

---

## Acceptance Criteria

- [ ] PM can upload a feedback CSV file
- [ ] Column mapping auto-detects common header names
- [ ] PM can adjust column mapping before import
- [ ] Preview shows first 5 rows mapped correctly
- [ ] Import processes all rows via Bulk API
- [ ] Failed rows are skipped, not fatal
- [ ] Import summary shows total/imported/failed counts
- [ ] PM can add feedback manually via form
- [ ] Manual feedback auto-analyzes sentiment
- [ ] PM can upload a customer CSV file
- [ ] Customer column mapping auto-detects headers
- [ ] PM can add customers manually via form
- [ ] Feedback list page shows all imported items with pagination
- [ ] Feedback list filters by source_type
- [ ] Customer list page shows all imported customers with pagination
- [ ] `{org_id}-feedback` index has ELSER semantic_text field
- [ ] `{org_id}-customers` index exists with correct mappings
- [ ] Upload history shows in Settings > Data Upload
- [ ] Onboarding sections B and C are functional
- [ ] All data filtered by org_id (multi-tenant verified)
- [ ] All backend tests pass
- [ ] All Phase 1 + Phase 2 tests still pass

---

## How to Give This to Cursor

> Read docs/PHASE_3_SPEC.md, PROJECT.md, and UX.md (Section B, Section C, Flow 8). This is the spec for Phase 3. The .cursorrules file applies. Do NOT start building yet. First, create a detailed implementation plan. Wait for my approval before writing any code.

---

## After Phase 3

Phase 4: Search + Feedback Page. Adds semantic search, hybrid queries, filters, feedback detail slide-out, customer profile page.
