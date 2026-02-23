# Phase 3 Checklist — Data Ingestion (Feedback + Customers)

> Walk through EVERY item below after Cursor finishes Phase 3.
> You need test CSV files. Create two simple ones before testing (instructions in Section A).
> Check the box only after you've verified it yourself.

---

## Pre-Check: Phase 1 + Phase 2 Still Work

- [ ] `docker compose up` starts without errors
- [ ] Log in → goes to /dashboard (not onboarding — you already completed it)
- [ ] Sidebar: all 6 nav links work
- [ ] Settings > Product Wizard → saved data from Phase 2 still there
- [ ] Agent chat bubble visible
- [ ] Dark/light theme toggle works

---

## A. Prepare Test Data

Create these two CSV files on your computer before testing.

### feedback_test.csv (save this)
```csv
feedback,source,company,date,rating
"The checkout flow is so confusing, I abandoned my cart twice",support_ticket,TechFlow Inc,2026-01-15,2
"Love the new dashboard! Makes my life easier",app_store_review,DataCorp,2026-01-18,5
"Payment keeps failing with my credit card",support_ticket,TechFlow Inc,2026-01-20,1
"Your search is slow and never finds what I need",nps_csat_survey,BigRetail Co,2026-02-01,2
"Great product overall but pricing is too high for SMBs",g2_capterra,SmallBiz Ltd,2026-02-05,3
"Dashboard crashes when I filter by date range",bug_report,DataCorp,2026-02-08,1
"Excellent customer support, resolved my issue in minutes",customer_email,MegaCorp,2026-02-10,5
"The mobile app is basically unusable",app_store_review,StartupX,2026-02-12,1
"Would love to see an API for bulk data exports",internal_team,,2026-02-14,
"Billing page shows wrong currency for international accounts",support_ticket,GlobalTech,2026-02-15,2
```

### customers_test.csv (save this)
```csv
company,segment,mrr,arr,account_manager,renewal_date,health_score,industry,employees
TechFlow Inc,enterprise,2500,30000,Sarah Chen,2026-04-15,72,fintech,450
DataCorp,enterprise,5000,60000,Mike Rodriguez,2026-06-01,85,analytics,800
BigRetail Co,enterprise,3500,42000,Sarah Chen,2026-03-20,45,retail,1200
SmallBiz Ltd,smb,200,2400,Automated,2026-12-01,60,saas,25
MegaCorp,enterprise,8000,96000,James Wilson,2026-08-15,91,enterprise,5000
StartupX,trial,0,0,,2026-03-01,30,mobile,10
GlobalTech,enterprise,4000,48000,Mike Rodriguez,2026-05-10,55,technology,650
```

---

## B. Feedback CSV Upload

### B1. Upload File
- [ ] Go to Settings > Data Upload (or onboarding Section B)
- [ ] See "Upload Feedback" section with drag-and-drop zone
- [ ] Drag `feedback_test.csv` onto the zone → file is accepted
- [ ] See filename "feedback_test.csv" and file size displayed
- [ ] Click "Upload"

### B2. Column Auto-Detection
- [ ] Column mapping screen appears
- [ ] "feedback" column auto-detected → mapped to "text" field (our feedback text)
- [ ] "source" column auto-detected → mapped to "source" field
- [ ] "company" column auto-detected → mapped to "customer_name" field
- [ ] "date" column auto-detected → mapped to "date" field
- [ ] "rating" column auto-detected → mapped to "rating" field
- [ ] Text field mapping shows as required (can't proceed without it)

### B3. Column Mapping Adjustment
- [ ] Change one mapping manually: unmap "company" from customer_name, pick a different mapping → it changes
- [ ] Change it back to customer_name
- [ ] Unmapped fields show as "None" or "Skip"
- [ ] Source type dropdown visible (for default source if not in CSV)
- [ ] "Auto-detect product areas" checkbox visible
- [ ] "Auto-analyze sentiment" checkbox visible
- [ ] Check both checkboxes

### B4. Preview
- [ ] First 5 rows of CSV shown in preview table
- [ ] Preview shows data mapped to correct columns
- [ ] "The checkout flow is so confusing..." appears under text column
- [ ] "support_ticket" appears under source column
- [ ] "TechFlow Inc" appears under customer column
- [ ] Row count shown: "10 items to import"

### B5. Import Execution
- [ ] Click "Import 10 items"
- [ ] Progress indicator shows (bar or spinner)
- [ ] Import completes successfully
- [ ] Summary shows: Total: 10, Imported: 10, Failed: 0

### B6. Auto-Detection Results
- [ ] After import, product area suggestions shown (if auto-detect was checked)
- [ ] Areas like "checkout", "dashboard", "payment", "search" suggested
- [ ] Each area shows count of matching feedback
- [ ] PM can confirm or reject each suggestion
- [ ] Confirming an area saves it (can verify in Settings > Product Wizard > Areas later)

### B7. Verify Data in Feedback List
- [ ] Go to Feedback page (click "Feedback" in sidebar)
- [ ] See all 10 imported items listed
- [ ] Each item shows: text (truncated), source badge (colored), sentiment indicator, date
- [ ] "support_ticket" items have correct source badge color
- [ ] "app_store_review" items have correct source badge color
- [ ] Pagination works (if you have >20 items from multiple imports)

---

## C. Feedback CSV — Edge Cases

### C1. Non-CSV File
- [ ] Try uploading a .txt file → rejected with clear error message
- [ ] Try uploading a .xlsx file → rejected with clear error message
- [ ] Try uploading a .png file → rejected

### C2. CSV with No Matching Headers
- [ ] Create a CSV with headers: `col_a,col_b,col_c`
- [ ] Upload → column mapping shows NO auto-detected fields
- [ ] PM must manually map at least the "text" column
- [ ] If PM doesn't map "text" → import button disabled or shows error

### C3. CSV with Missing Data
- [ ] Create a CSV where some rows have empty fields (e.g., no date, no company)
- [ ] Upload and import → import succeeds
- [ ] Items with missing fields show null/empty for those fields (not crash)

### C4. CSV with Bad Rows
- [ ] Create a CSV with one row that has completely garbled data
- [ ] Upload and import → import completes
- [ ] Failed row count = 1, imported = rest
- [ ] Summary clearly shows the failure count

### C5. Large CSV (if feasible)
- [ ] Create a CSV with 100+ rows (duplicate the test data)
- [ ] Upload and import → all rows imported via Bulk API
- [ ] Verify count in feedback list matches

### C6. Duplicate Import
- [ ] Upload the same `feedback_test.csv` again
- [ ] Import completes (items added — dedup may or may not apply depending on implementation)
- [ ] No crash or error

---

## D. Feedback Manual Entry

### D1. Full Entry
- [ ] Go to Feedback page or Settings > Data Upload > Manual Entry tab
- [ ] See textarea for feedback text (required)
- [ ] See source dropdown with all 11 source types:
  - [ ] App Store Review
  - [ ] G2 / Capterra Review
  - [ ] Support Ticket
  - [ ] NPS / CSAT Survey
  - [ ] Customer Email
  - [ ] Sales Call Note
  - [ ] Slack Message
  - [ ] Internal Team Feedback
  - [ ] User Interview / Research
  - [ ] Bug Report (Jira/Linear)
  - [ ] Community Forum / Discord
- [ ] Product area dropdown shows areas from wizard (+ "Other"/"New")
- [ ] Customer search/input field
- [ ] Author name field
- [ ] Author email field
- [ ] Date picker (defaults to today)
- [ ] Rating selector (1-5 stars)

### D2. Submit Minimal
- [ ] Enter only text: "This is a test feedback entry"
- [ ] Click "Add Feedback"
- [ ] Success message shown
- [ ] Item appears in feedback list

### D3. Submit Full
- [ ] Enter text: "Billing is confusing for enterprise customers"
- [ ] Select source: "Customer Email"
- [ ] Select product area: (one from your wizard)
- [ ] Enter author name: "Jane Doe"
- [ ] Enter author email: "jane@example.com"
- [ ] Select date: yesterday
- [ ] Set rating: 2
- [ ] Click "Add Feedback"
- [ ] Success → item appears in list with all fields

### D4. Validation
- [ ] Try submitting with empty text → validation error shown
- [ ] Error shows under the text field, not a generic alert

### D5. Auto-Sentiment
- [ ] Submit text: "This product is absolutely terrible and broken"
- [ ] Check the created item → sentiment should be "negative" with negative score
- [ ] Submit text: "I love this product, it's amazing and fast"
- [ ] Check → sentiment "positive" with positive score
- [ ] Submit text: "The product exists"
- [ ] Check → sentiment "neutral" with ~0 score

### D6. "Add Another" Flow
- [ ] Check "Add another" checkbox before submitting
- [ ] Submit feedback → form clears, stays on form (doesn't navigate away)
- [ ] Submit another one → works again

---

## E. Customer CSV Upload

### E1. Upload File
- [ ] Go to Settings > Data Upload (or onboarding Section C)
- [ ] See "Upload Customers" section
- [ ] Upload `customers_test.csv`

### E2. Column Auto-Detection
- [ ] "company" → auto-detected as company_name
- [ ] "segment" → auto-detected
- [ ] "mrr" → auto-detected
- [ ] "arr" → auto-detected
- [ ] "account_manager" → auto-detected
- [ ] "renewal_date" → auto-detected
- [ ] "health_score" → auto-detected
- [ ] "industry" → auto-detected
- [ ] "employees" → auto-detected as employee_count

### E3. Preview + Import
- [ ] Preview shows first 5 rows mapped correctly
- [ ] "TechFlow Inc" in company column, "enterprise" in segment, "$2,500" in MRR
- [ ] Click Import → success
- [ ] Summary: Total: 7, Imported: 7, Failed: 0

### E4. Verify in Customers List
- [ ] Go to Customers page (sidebar)
- [ ] See 7 customers listed
- [ ] Table shows: company name, segment badge, MRR, ARR, health (colored), renewal date
- [ ] TechFlow Inc → enterprise badge, $2,500 MRR, health 72 (yellow)
- [ ] MegaCorp → enterprise, $8,000 MRR, health 91 (green)
- [ ] StartupX → trial badge, $0 MRR, health 30 (red)
- [ ] BigRetail Co → renewal date Mar 20 should show warning (within 60 days of today)

---

## F. Customer Manual Entry

### F1. Full Entry
- [ ] Go to customer manual entry form
- [ ] Enter company name: "ManualCo" (required)
- [ ] Select segment: "smb"
- [ ] Enter MRR: 500
- [ ] Enter ARR: 6000
- [ ] Enter account manager: "Test Person"
- [ ] Enter renewal date
- [ ] Enter health score: 65
- [ ] Enter industry: "technology"
- [ ] Enter employee count: 100
- [ ] Click "Add Customer" → success

### F2. Minimal Entry
- [ ] Enter only company name: "MinimalCo"
- [ ] Click "Add Customer" → success
- [ ] Check in list → shows with empty/null for optional fields

### F3. Validation
- [ ] Submit with empty company name → error shown

---

## G. Feedback List Page (Functional)

### G1. List Display
- [ ] Shows all feedback items (from CSV + manual entries)
- [ ] Each item: text preview (truncated ~2 lines), source badge, sentiment dot, area tag, date
- [ ] Source badges are color-coded by type
- [ ] Sentiment dots: green (positive), red (negative), gray (neutral)

### G2. Pagination
- [ ] If >20 items, pagination controls appear
- [ ] Click page 2 → shows next set of items
- [ ] "Showing X of Y items" count is accurate

### G3. Filters
- [ ] Source type filter dropdown works
- [ ] Select "support_ticket" → only support ticket items shown
- [ ] Select "app_store_review" → only app store items
- [ ] Clear filter → all items shown again

### G4. Sorting
- [ ] Sort by date (newest first) → most recent items on top
- [ ] Sort by date (oldest first) → oldest items on top
- [ ] Sort by sentiment (most negative) → lowest scores first

### G5. Empty State
- [ ] Log in as a DIFFERENT user (new org) who has no data
- [ ] Feedback page shows empty state: "No feedback yet. Import data to start analyzing."
- [ ] CTA buttons: [Upload CSV] [Add Manually]

---

## H. Customers List Page (Functional)

### H1. List Display
- [ ] Shows all customers from CSV + manual entries
- [ ] Table: company name, segment, MRR, ARR, health (colored), renewal
- [ ] Health colors: green (70+), yellow (40-69), red (<40)

### H2. Pagination
- [ ] Pagination works if >20 customers

### H3. Filters
- [ ] Segment filter works
- [ ] Select "enterprise" → only enterprise customers
- [ ] Clear → all customers

### H4. Empty State
- [ ] New user with no customers sees: "No customers yet. Upload data to connect feedback to revenue."

---

## I. Settings > Data Upload

- [ ] Go to Settings → Data Upload tab
- [ ] See "Upload Feedback" section with CSV + manual tabs
- [ ] See "Upload Customers" section with CSV + manual tabs
- [ ] Upload History table below:
  - [ ] Shows previous uploads with: Date, Type (feedback/customers), Filename, Items Imported, Status
  - [ ] feedback_test.csv shows with status "completed", items: 10
  - [ ] customers_test.csv shows with status "completed", items: 7

---

## J. Onboarding Sections B + C

- [ ] Sign up as a NEW user
- [ ] Complete product wizard (or skip)
- [ ] Section B (Upload Feedback) is now active/clickable
- [ ] Can upload a CSV through onboarding flow
- [ ] After feedback upload → Section C (Upload Customers) becomes active
- [ ] Can upload customers through onboarding flow
- [ ] After all three sections → "Finish Setup → Go to Dashboard"
- [ ] Goes to dashboard, never shows onboarding again

---

## K. ELSER / Elasticsearch Verification

### K1. ELSER Deployment
- [ ] Open Kibana → Dev Tools
- [ ] Run: `GET _inference/elser-endpoint` → should return model info (not 404)
- [ ] ELSER inference endpoint is active

### K2. Feedback Index
- [ ] Run: `GET {org_id}-feedback/_mapping`
- [ ] Confirm `text_semantic` field has type `semantic_text`
- [ ] Confirm `inference_id` references the ELSER endpoint
- [ ] Run: `GET {org_id}-feedback/_count` → matches your imported count
- [ ] Run: `GET {org_id}-feedback/_search?size=1` → document has all expected fields:
  - [ ] id, org_id, text, text_semantic, source, sentiment, sentiment_score
  - [ ] product_area, customer_name, author_name, ingestion_method, created_at, ingested_at

### K3. Customers Index
- [ ] Run: `GET {org_id}-customers/_mapping` → correct field types
- [ ] Run: `GET {org_id}-customers/_count` → matches imported count
- [ ] Run: `GET {org_id}-customers/_search?size=1` → document has expected fields

### K4. Upload History Index
- [ ] Run: `GET upload-history/_search?q=org_id:{org_id}` → shows your uploads
- [ ] Each upload document has: upload_type, filename, total_rows, imported_rows, status

### K5. Multi-Tenant Isolation
- [ ] Run: `GET {org_A_id}-feedback/_count` → Org A's feedback count
- [ ] Run: `GET {org_B_id}-feedback/_count` → Org B's feedback count (different or 0)
- [ ] Org A can NOT see Org B's data via API

---

## L. API Verification (curl or devtools)

### L1. Feedback Endpoints
- [ ] `POST /api/v1/feedback/manual` with `{"text":"test"}` → 200, returns item
- [ ] `POST /api/v1/feedback/manual` with `{}` → 422
- [ ] `GET /api/v1/feedback` → paginated list with `data` + `pagination`
- [ ] `GET /api/v1/feedback?source_type=support_ticket` → filtered results
- [ ] `GET /api/v1/feedback/{id}` → single item
- [ ] `GET /api/v1/feedback/{id}` with wrong org's item → 404
- [ ] `GET /api/v1/feedback/count` → `{ "data": { "count": N } }`

### L2. Customer Endpoints
- [ ] `POST /api/v1/customers/manual` with `{"company_name":"Test"}` → 200
- [ ] `POST /api/v1/customers/manual` with `{}` → 422
- [ ] `GET /api/v1/customers` → paginated list
- [ ] `GET /api/v1/customers/{id}` → single customer
- [ ] `GET /api/v1/customers/{id}` wrong org → 404
- [ ] `GET /api/v1/customers/count` → correct count

### L3. Upload Endpoints
- [ ] `GET /api/v1/uploads` → list of past uploads for this org
- [ ] `GET /api/v1/uploads/{id}` → single upload with status + counts

### L4. Auth Required
- [ ] Any endpoint without JWT → 401

---

## M. Sentiment Analysis Verification

- [ ] Find the feedback "Love the new dashboard! Makes my life easier" → sentiment: positive, score > 0
- [ ] Find "Payment keeps failing with my credit card" → sentiment: negative, score < 0
- [ ] Find "Would love to see an API for bulk data exports" → check sentiment (could be neutral or slightly positive)
- [ ] Manually entered "terrible and broken" text → negative
- [ ] Manually entered "amazing and fast" text → positive
- [ ] Sentiment scores are in range -1.0 to 1.0

---

## N. Edge Cases

- [ ] Upload empty CSV (headers only, no data rows) → handled gracefully (0 imported, no crash)
- [ ] Upload CSV with 1 row → imports correctly
- [ ] Upload very long feedback text (1000+ characters) → saved and displayed correctly
- [ ] Upload CSV with Unicode/special characters (é, ñ, 日本語) → handled
- [ ] Upload CSV with commas inside quoted fields → parsed correctly
- [ ] Enter MRR as 0 for a customer → saves correctly (no error)
- [ ] Enter health_score as 0 → saves correctly
- [ ] Enter health_score as 100 → saves correctly
- [ ] Enter negative MRR → either rejected or stored (verify which)
- [ ] Upload same CSV twice → no crash (may create duplicates — acceptable for now)

---

## O. UI/UX Quality

- [ ] Drag-and-drop zone has clear visual feedback (highlight on hover/drag)
- [ ] File type restriction message visible ("CSV files only")
- [ ] Column mapping dropdowns styled in dark mode
- [ ] Preview table readable in dark mode
- [ ] Progress bar visible during import
- [ ] Success message clearly shows imported/failed counts
- [ ] Source badges have distinct colors per type
- [ ] Sentiment dots are clearly green/red/gray
- [ ] Feedback text truncation with "..." works
- [ ] Date displays as relative ("2 days ago") or formatted nicely
- [ ] Customer health scores color-coded (green/yellow/red)
- [ ] Renewal date warnings show for dates within 60 days
- [ ] All new pages work in both dark and light mode
- [ ] No layout shifts during loading
- [ ] Agent chat bubble still visible on all new pages

---

## P. Backend Tests

- [ ] Run: `docker compose exec backend pytest`
- [ ] All Phase 1 tests pass
- [ ] All Phase 2 tests pass
- [ ] All Phase 3 tests pass:
  - [ ] test_feedback_service.py (9 tests)
  - [ ] test_customer_service.py (7 tests)
  - [ ] test_csv_service.py (7 tests)
  - [ ] test_feedback_routes.py (9 tests)
  - [ ] test_customer_routes.py (6 tests)
  - [ ] test_upload_service.py (3 tests)
  - [ ] test_sentiment.py (3 tests)
- [ ] No test failures

---

## Q. Frontend Build

- [ ] No TypeScript errors: `docker compose exec frontend npx tsc --noEmit`
- [ ] No console errors in browser during normal usage
- [ ] No React warnings about uncontrolled inputs or missing keys

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| Pre-Check (Phase 1+2) | 6 | [ ] |
| A. Prepare Test Data | 2 files | [ ] |
| B. Feedback CSV Upload | 20 | [ ] |
| C. Feedback CSV Edge Cases | 10 | [ ] |
| D. Feedback Manual Entry | 15 | [ ] |
| E. Customer CSV Upload | 14 | [ ] |
| F. Customer Manual Entry | 5 | [ ] |
| G. Feedback List Page | 12 | [ ] |
| H. Customers List Page | 7 | [ ] |
| I. Settings > Data Upload | 6 | [ ] |
| J. Onboarding B + C | 7 | [ ] |
| K. ELSER / ES Verification | 14 | [ ] |
| L. API Verification | 12 | [ ] |
| M. Sentiment Verification | 6 | [ ] |
| N. Edge Cases | 10 | [ ] |
| O. UI/UX Quality | 15 | [ ] |
| P. Backend Tests | 10 | [ ] |
| Q. Frontend Build | 3 | [ ] |
| **TOTAL** | **~170** | |

**Phase 3 is DONE when every box above is checked.**
