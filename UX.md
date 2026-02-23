# UX.md — Context Engine v2: Complete User Experience

> Source of truth for how the product works from the user's perspective.
> Every screen, every interaction, every flow.
> Read this BEFORE writing any frontend or API code.

---

## App Overview

- **What:** Feedback intelligence platform for Product Managers
- **Access:** Web app via browser (localhost:3000 dev, deployed URL prod)
- **Setup:** git clone → docker compose up → open browser
- **Auth:** Email/password login, JWT-based
- **Theme:** Dark mode default, light mode toggle
- **Navigation:** Left sidebar with text labels (Jira-style)
- **Agent Chat:** Always-visible floating sidebar panel (Intercom-style), accessible from every page
- **Desktop-first:** Responsive but optimized for desktop

---

## User Type

| Role | Description |
|------|------------|
| **Product Manager** | Only user type. Full access. Monitors feedback, investigates issues, configures product, generates specs. |

> Future roles (not now): Engineering Lead, Customer Success, Admin.

---

## Screen Map

    Login / Sign Up
      │
      ├── First time? → Onboarding
      │     ├── Product Wizard (8 steps, all skippable)
      │     ├── Upload Feedback (CSV + manual)
      │     └── Upload Customers (CSV + manual)
      │
      └── Returning? → Dashboard (home)

    Left Sidebar (always visible):
      ├── Dashboard        ← home, customizable widgets
      ├── Feedback         ← search, browse, filter, slide-out detail
      ├── Customers        ← list, full profiles, risk, revenue
      ├── Specs            ← saved spec history, 4-tab viewer, download
      ├── Analytics        ← Kibana embedded / linked
      └── Settings
           ├── Product Wizard  ← same 8-step wizard, editable anytime
           ├── Data Upload     ← feedback + customer upload
           ├── Connectors      ← Slack + future integrations
           ├── Account         ← email, password, theme
           └── Elasticsearch   ← connection status, index stats

    Floating (every page):
      └── Agent Chat       ← right sidebar panel

---

## Flow 1: Auth

### Login (/login)
- Email input
- Password input
- "Log in" button
- "Sign up" link
- "Forgot password" link (future)

### Sign Up (/signup)
- Email
- Password + confirm
- Organization name
- "Create Account" → goes to Onboarding

### Session
- JWT token, stored in httpOnly cookie
- Auto-redirect to /login if expired
- After login: first time → Onboarding, returning → Dashboard

---

## Flow 2: Onboarding (First Time)

### Trigger
First login. No data exists yet.

### Welcome Screen
- "Welcome to Context Engine! Let's set up your product."
- Three sections shown as progress: Product → Feedback → Customers
- "Skip everything and explore" link at bottom

---

### Section A: Product Wizard (8 Steps)

Same wizard is available in Settings > Product Wizard at any time. PM can revisit, edit, add more. Every step is skippable.

Progress bar at top: Step 1 of 8 ● ● ● ○ ○ ○ ○ ○

---

#### Step 1: Product Basics

| Field | Type | Required | Example |
|-------|------|----------|---------|
| Product name | Text | Yes (only required field in entire wizard) | "Acme Analytics" |
| Description | Textarea | No | "B2B SaaS data analytics platform for mid-market companies" |
| Industry | Dropdown | No | SaaS, Fintech, Healthcare, E-commerce, Education, Other |
| Stage | Dropdown | No | Early stage, Growth, Mature, Enterprise |
| Website URL | Text | No | "https://acme-analytics.com" |

Actions: Continue / Skip / Back

---

#### Step 2: Product Areas / Modules

Purpose: Define the parts of your product so feedback can be categorized.

| Field | Type | Example |
|-------|------|---------|
| Area name | Text | "Checkout Flow" |
| Description | Text | "Multi-step purchase and payment flow" |

- "Add area" button to add more
- Minimum 0, no maximum
- Can reorder via drag-and-drop
- PM can also let the system auto-detect areas later from uploaded feedback

Hint text: "Don't worry about getting these perfect. We'll suggest more areas once you upload feedback."

Actions: Continue / Skip / Back

---

#### Step 3: Business Goals / OKRs

Purpose: Agent uses this to connect feedback to strategic priorities.

| Field | Type | Example |
|-------|------|---------|
| Time period | Dropdown | Q1 2026, Q2 2026, H1 2026, Custom |
| Goal title | Text | "Reduce checkout abandonment by 30%" |
| Goal description | Textarea | "Checkout drop-off is our #1 growth bottleneck" |
| Priority | Dropdown | P0 (Critical), P1 (High), P2 (Medium), P3 (Low) |
| Linked product area | Dropdown (from Step 2) | "Checkout Flow" |

- "Add goal" button for multiple goals
- Agent uses these to say things like: "This aligns with your Q1 goal of reducing checkout abandonment"

Actions: Continue / Skip / Back

---

#### Step 4: Customer Segments + Pricing

Purpose: Agent uses this to calculate revenue impact and segment analysis.

Customer Segments:
| Field | Type | Example |
|-------|------|---------|
| Segment name | Text | "Enterprise" |
| Description | Text | "Companies with 500+ employees" |
| Revenue share | Percentage | 60% |

- Default segments pre-filled: Enterprise, SMB, Consumer, Trial
- PM can rename, add, remove

Pricing Tiers:
| Field | Type | Example |
|-------|------|---------|
| Tier name | Text | "Enterprise Pro" |
| Price | Currency | $2,500/month |
| Segment | Dropdown | Enterprise |
| Features summary | Text | "Unlimited users, SSO, dedicated support" |

Actions: Continue / Skip / Back

---

#### Step 5: Competitors

Purpose: Agent references competitors when generating specs ("Competitor X solves this by...").

| Field | Type | Example |
|-------|------|---------|
| Competitor name | Text | "Mixpanel" |
| Website | Text | "https://mixpanel.com" |
| Strengths | Textarea | "Great funnel analytics, fast UI" |
| Weaknesses | Textarea | "No feedback integration, expensive at scale" |
| How we differentiate | Textarea | "We combine analytics with customer voice" |

- "Add competitor" button for multiple
- Agent uses this for competitive context in specs

Actions: Continue / Skip / Back

---

#### Step 6: Roadmap

Purpose: Agent knows what's planned vs what exists, avoids suggesting features already in progress.

Two sections:

Existing Features:
| Field | Type | Example |
|-------|------|---------|
| Feature name | Text | "Basic Dashboard" |
| Product area | Dropdown | "Dashboard" |
| Status | Dropdown | Live, Beta, Deprecated |
| Release date | Date | Jan 2025 |

Planned Features:
| Field | Type | Example |
|-------|------|---------|
| Feature name | Text | "Advanced Filtering" |
| Product area | Dropdown | "Dashboard" |
| Status | Dropdown | Planned, In Progress, Blocked |
| Target date | Date | Q2 2026 |
| Priority | Dropdown | P0-P3 |

- Agent uses this to say: "Note: Advanced Filtering is already planned for Q2. Consider bundling this fix with that initiative."

Actions: Continue / Skip / Back

---

#### Step 7: Team Structure

Purpose: Agent assigns ownership when generating specs.

| Field | Type | Example |
|-------|------|---------|
| Team name | Text | "Payments Team" |
| Team lead | Text | "Mike Rodriguez" |
| Owns product areas | Multi-select (from Step 2) | Checkout Flow, Pricing |
| Size | Number | 6 |
| Slack channel | Text | #team-payments |

- "Add team" button for multiple teams
- Agent uses this for: "Recommended owner: Payments Team (Mike Rodriguez)"

Actions: Continue / Skip / Back

---

#### Step 8: Tech Stack

Purpose: Agent includes technical context in Architecture docs.

| Field | Type | Example |
|-------|------|---------|
| Category | Dropdown | Frontend, Backend, Database, Infrastructure, Monitoring, Other |
| Technology | Text | "React 18" |
| Notes | Text | "With Next.js, deployed on Vercel" |

- Pre-filled categories, PM fills in technologies
- Common stacks as templates: "SaaS Starter (React + Node + Postgres)"
- Agent uses this in Architecture spec: "Current frontend is React 18 on Next.js..."

Actions: Finish / Skip / Back

---

#### After Wizard Complete
- "Product setup complete! Now let's add some feedback."
- Continue to Feedback Upload
- Or "Skip to Dashboard"

---

### Section B: Upload Feedback

Purpose: Get feedback data into the system.

Two tabs:

#### Tab 1: CSV Upload
1. Drag-and-drop zone or file picker
2. After file selected → Column Mapping Screen:
   - "Which column is the feedback text?" → dropdown of CSV columns (required)
   - "Date?" → dropdown (or "Use today's date")
   - "Source?" → dropdown (or select from our source list)
   - "Product area?" → dropdown (or "Auto-detect from content")
   - "Customer name/ID?" → dropdown (or "No customer data in this file")
   - "Sentiment?" → dropdown (or "Auto-analyze sentiment")
3. Preview: First 5 rows shown mapped to fields
4. "Import X items" button
5. Progress bar during import
6. Success screen:
   - "Imported 800 feedback items"
   - "Auto-detected 6 product areas: checkout (102), pricing (78), dashboard (61)..."
   - PM can confirm, rename, merge, or reject each detected area
   - Detected areas merge with any from Product Wizard Step 2

#### Tab 2: Manual Entry
- Feedback text (textarea, required)
- Source (dropdown — see source list below)
- Product area (dropdown of existing + "Other/New")
- Customer (search existing or leave blank)
- Date (date picker, defaults to now)
- Rating (1-5 stars, optional)
- "Add Feedback" button
- "Add another" checkbox to stay on form

Feedback Source List (all 11):
| Source | Type | Tag Color |
|--------|------|-----------|
| App Store Review | External customer | Blue |
| G2 / Capterra Review | External customer | Blue |
| Support Ticket | External customer | Orange |
| NPS / CSAT Survey | External customer | Green |
| Customer Email | External customer | Orange |
| Sales Call Note | Internal + customer | Purple |
| Slack Message | Internal team | Yellow |
| Internal Team Feedback | Internal team | Yellow |
| User Interview / Research | Research | Brown |
| Bug Report (Jira/Linear) | Technical | Red |
| Community Forum / Discord | Community | Gray |

Auto-detection after upload:
- System analyzes feedback text → suggests product areas
- System analyzes sentiment → assigns positive/negative/neutral + score
- System detects source patterns if not specified

Actions: Continue to Customers / Skip to Dashboard

---

### Section C: Upload Customers

Same pattern as Feedback Upload (CSV + Manual).

CSV Column Mapping:
- Company name (required)
- Customer ID (for linking with feedback)
- Segment (dropdown: maps to segments from Wizard Step 4)
- MRR / ARR
- Account manager
- Renewal date
- Industry
- Health score
- Employee count
- Plan/tier (maps to pricing from Wizard Step 4)

Manual Entry:
- All fields in a form
- "Add Customer" button

Actions: "Finish Setup → Go to Dashboard"

---

## Flow 3: Dashboard (/dashboard)

Home page. What the PM sees every day.

### Top Bar
- Date range selector (7d / 30d / 90d / custom) — applies to all widgets
- "Customize Dashboard" button → dropdown with checkboxes to show/hide widgets
- Refresh button

### Dashboard Widgets (all visible by default, customizable)

Widget 1: Summary Cards (top row, 4 cards)
| Total Feedback | Avg Sentiment | Active Issues | At-Risk Customers |
|---|---|---|---|
| 847 ↑12% | -0.23 ↓5% | 4 Critical | 3 accounts |
- Each card shows value + trend arrow vs previous period
- Clickable: goes to relevant page

Widget 2: Feedback Volume Over Time
- Line chart, configurable period (7d/30d/90d)
- Can overlay multiple product areas (toggle lines)
- Hover for daily counts
- Click point → goes to Feedback filtered by that day

Widget 3: Sentiment Breakdown
- Donut chart: positive % / negative % / neutral %
- Clickable segments → Feedback page filtered by sentiment

Widget 4: Top Issues (ranked cards)
- Top 3-5 issues, each showing:
  - Issue name (e.g., "Checkout: Form State Loss")
  - Feedback count + growth rate (↑23% this week)
  - Severity badge: Critical / Emerging / Stable / Improving
  - Affected customers count + total ARR
  - "Investigate" button → opens Agent Chat pre-filled
  - "Generate Spec" button → opens Agent Chat pre-filled

Widget 5: Product Area Breakdown
- Horizontal bar chart: feedback count per product area
- Bars color-coded by average sentiment
- Clickable → Feedback page filtered by area

Widget 6: At-Risk Customers
- Table of enterprise customers with negative feedback patterns
- Columns: Company, ARR, Negative Feedback (30d), Renewal, Health
- Warning icon on renewal dates within 60 days
- Health colors: green 70+, yellow 40-69, red <40
- Click row → Customer profile page

Widget 7: Recent Feedback Stream
- Latest 10 items, live-updating feel
- Each: text preview (2 lines), source badge, sentiment dot, product area tag, time ago
- Click → opens Feedback detail slide-out

Widget 8: Source Distribution
- Pie chart showing feedback by source
- Shows which channels produce the most feedback
- Clickable → Feedback page filtered by source

Widget 9: Feedback by Segment
- Stacked bar or grouped bar: enterprise vs SMB vs consumer vs trial
- Per product area or overall
- Helps PM see which segment is hurting most

---

## Flow 4: Feedback Page (/feedback)

### Layout
List on left (~70%), detail slide-out panel on right (~30%) when item selected.

### Search Bar (prominent, top)
- Semantic search: PM types natural language
- "payment problems" finds "checkout broken", "credit card declined", "billing confusion"
- Real-time results as you type (debounced)

### Filters (below search)
- Product area: multi-select dropdown
- Source: multi-select dropdown (all 11 sources)
- Sentiment: positive / negative / neutral toggle buttons
- Customer segment: enterprise / SMB / consumer / trial
- Date range: presets (7d, 30d, 90d) + custom picker
- Customer: search by company name
- Has customer linked: yes / no
- "Clear all filters" link
- Filter state reflected in URL (shareable filtered views)

### Results List
Each item shows:
- Feedback text (first 2 lines, truncated)
- Source badge (colored pill)
- Sentiment indicator (green/red/gray dot + score)
- Product area tag
- Customer name (if linked, clickable)
- Date (relative: "2 days ago")

Sort by: Relevance (default when searching), Date (newest), Sentiment (most negative first)
Pagination: Infinite scroll or "Load more"
Count: "Showing 47 of 847 items"

### Feedback Detail (Right Slide-Out)

Triggered by: clicking any item in list.

Content:
- Full feedback text (untruncated)
- Source with colored icon
- Sentiment: score + label (e.g., -0.72 Negative)
- Product area tag
- Rating (if available, shown as stars)
- Date submitted
- Ingestion source (CSV upload, manual entry, Slack connector)

Customer Card (if linked):
- Company name (clickable → Customer page)
- Segment badge
- MRR / ARR
- Health score
- Account manager
- Renewal date (warning if within 60 days)

Similar Feedback:
- "5 similar items found" — vector similarity from ES
- Preview of each, clickable to swap detail panel

Actions:
- "Ask agent about this" → opens Agent Chat
- "Generate spec" → opens Agent Chat
- "Copy text" → clipboard
- "Star" / "Flag" for later reference

Close: X button, click outside, or Escape key

---

## Flow 5: Customers Page (/customers)

### Customer List (/customers)

Search: by company name, account manager, industry

Filters:
- Segment: enterprise / SMB / consumer / trial
- Health score range: slider 0-100
- Renewal: within 30d / 60d / 90d / all
- Has negative feedback: yes / no
- ARR range: min-max

Table:
| Company Name | Segment | MRR | ARR | Health | Feedback Count | Renewal |
|---|---|---|---|---|---|---|
| TechFlow Inc | Enterprise | $2,500 | $30,000 | 72 yellow | 12 (5 negative) | Apr 15 warning |

- Sortable columns
- Click row → Customer Profile page

### Customer Profile (/customers/{id})

Header:
- Company name (large)
- Segment badge + Plan name
- Industry tag

Key Metrics (card row):
| MRR | ARR | Health Score | Total Feedback | Avg Sentiment | Days to Renewal |
|---|---|---|---|---|---|
| $2,500 | $30,000 | 72 yellow | 12 | -0.34 red | 54 warning |

Account Details:
- Account manager
- Employee count
- Created date
- Renewal date (highlighted if within 60 days)
- Plan/tier

Sentiment Trend (chart):
- Line chart: this customer's sentiment over time
- Overlay with product average for comparison

Feedback History:
- All feedback from this customer
- Same card format as Feedback page
- Filter by product area, sentiment, date
- Click → feedback detail slide-out

Specs Mentioning This Customer:
- List of generated specs that cited this customer's feedback
- Click → Spec detail page

Actions:
- "Ask agent about this customer" → Agent Chat
- "View all feedback" → Feedback page pre-filtered
- "View in Kibana" → opens Kibana filtered

---

## Flow 6: Specs Page (/specs)

### Specs List (/specs)

Saved specs listed as cards:
- Title (e.g., "Checkout Flow Fix")
- Product area tag
- Date generated
- Feedback items cited count
- Status badge: Draft / Final / Shared
- PRD first paragraph preview

Sort: Date (newest first), product area
Filter: Product area, status, date range

"Generate New Spec" button → opens Agent Chat with prompt

### Spec Detail (/specs/{id})

4-Tab Navigation: [ PRD ] [ Architecture ] [ Rules ] [ Plan ]

Each tab renders:
- Full markdown content, beautifully styled
- Headings, lists, tables, code blocks
- Highlighted quotes from real feedback (clickable → opens feedback detail)
- Customer names and ARR where cited (clickable → customer profile)
- Product context references ("Aligned with Q1 goal: Reduce checkout abandonment")
- Competitor mentions ("Competitor X handles this by...")
- Team assignments ("Recommended owner: Payments Team")

Sidebar Metadata:
- Generated by: Context Engine Agent
- Date generated
- Feedback items analyzed: 47
- Customers cited: 12
- Product area: checkout
- Data freshness: "Based on feedback through Feb 18, 2026"
- Linked business goal (if any)

Actions:
- "Download All" → 4 markdown files as zip, or single PDF
- "Download [current tab]" → single markdown or PDF
- "Copy to Clipboard" → current tab markdown
- "Share" → generates shareable link
- "Regenerate" → sends to Agent Chat
- "Edit" → inline editing of generated content
- "Change Status" → Draft → Final → Shared

---

## Flow 7: Analytics Page (/analytics)

Kibana Embedded + Linked

Sub-tabs:

Tab 1: Feedback Overview
- Kibana dashboard (iframe): volume, sources, areas, sentiment

Tab 2: Trends and Alerts
- Kibana dashboard (iframe): sentiment by area over time, week-over-week, growing issues

Tab 3: Deep Dive
- Kibana dashboard (iframe): fully filterable, individual items

Tab 4: Custom
- "Open Kibana in new tab" for power users
- Instructions for creating custom dashboards

Top bar: Date range selector + "Open in Kibana" link

---

## Flow 8: Settings (/settings)

### Settings > Product Wizard
- Same 8-step wizard from onboarding
- All data pre-filled from previous entries
- Can edit any step, changes save immediately
- Agent system prompt auto-updates when product info changes

### Settings > Data Upload
- Upload Feedback (same CSV + manual UI)
- Upload Customers (same CSV + manual UI)
- Upload History table: Date, Type, File, Items, Status

### Settings > Connectors
- Slack (available now):
  - Connect workspace → select channels
  - Auto-ingest messages as feedback
  - Toggle on/off
- Future connectors shown as "Coming Soon":
  - Zendesk / Intercom, Jira / Linear, G2 / Capterra
  - "Notify me when available"

### Settings > Account
- Email, change password
- Theme toggle (dark/light)
- Dashboard preferences
- Organization name
- "Delete account" with confirmation

### Settings > Elasticsearch
- Connection status indicator
- Cluster name and version
- Index stats table: Index, Documents, Size
- "Re-index all" button
- "Clear all data" button (destructive, requires typing DELETE)
- Kibana URL link

---

## Flow 9: Agent Chat (Always Available)

### Trigger
Floating chat bubble (bottom-right, every page). Click to expand sidebar panel.

### Layout
Right sidebar panel, ~400px wide. Slides from right. Resizable. Minimizable to bubble.

### Header
- "Context Engine Agent" with icon
- Minimize, New conversation, History dropdown

### Messages
- User: right-aligned, accent color
- Agent: left-aligned, styled markdown, inline data cards, tool indicators, citations, action buttons

### Input
- Text input: "Ask me anything about your feedback..."
- Send button + Enter key

### Suggested Prompts (when empty)
- "What's happening with checkout this week?"
- "What should we prioritize this quarter?"
- "Show me feedback from enterprise customers"
- "Compare pricing sentiment: enterprise vs SMB"
- "Generate specs for [top issue]"
- "Which customers are at risk?"

### Agent Capabilities
1. Search: "Find feedback about payment problems"
2. Trends: "Is checkout getting worse?"
3. Comparison: "Compare enterprise vs SMB on pricing"
4. Investigation: "What's going on with dashboard performance?"
5. Prioritization: "What should we fix first?"
6. Customer lookup: "Show me TechFlow's feedback"
7. Spec generation: "Generate specs for fixing checkout"
8. Explain: "Why is sentiment dropping?"
9. Product context: "How does this relate to our Q1 goals?"
10. Competitive: "How do competitors handle checkout?"

### Agent Context (what agent knows at all times)
- All feedback data (via ES search tools)
- All customer data (via ES search tools)
- Product info (injected into system prompt):
  - Product basics, areas, teams
  - Business goals / OKRs
  - Customer segments + pricing
  - Competitors + differentiation
  - Roadmap (planned vs existing)
  - Tech stack
- Past conversation history (within session)
- Past generated specs

### Spec Generation Flow
1. PM: "Generate specs for checkout"
2. Agent: "Searching feedback about checkout... found 102 items"
3. Agent: "Analyzing: 5 sub-issues, 23 enterprise customers affected ($450K ARR)"
4. Agent: "Generating 4 spec documents..."
5. Agent shows summary with [View Full Specs] link
6. Click → navigates to /specs/{new_id}
7. Spec auto-saved to history

### Context-Aware Pre-fills
- Dashboard "Investigate" → "Tell me more about [issue]"
- Dashboard "Generate Spec" → "Generate specs for [issue]"
- Feedback detail → "Analyze this feedback and find related issues"
- Customer profile → "What's the situation with [company]?"
- Spec "Regenerate" → "Regenerate specs for [topic]"

---

## Component: Left Sidebar

    ┌──────────────────────┐
    │  ◆ Context Engine    │  ← Logo + name
    │──────────────────────│
    │                      │
    │  Dashboard           │  ← Bold when active
    │  Feedback            │
    │  Customers           │
    │  Specs               │
    │  Analytics           │
    │                      │
    │──────────────────────│
    │                      │
    │  Settings            │  ← Bottom section
    │  Theme toggle        │
    │  User + logout       │
    │                      │
    └──────────────────────┘

- Active page: accent color + background highlight
- Collapsible to icon-only mode
- Agent chat bubble floats outside sidebar (bottom-right of content)

---

## Empty States

| Page | Message | CTA |
|------|---------|-----|
| Dashboard | "No data yet. Set up your product and upload feedback." | [Start Product Wizard] [Upload Feedback] |
| Feedback | "No feedback yet. Import data to start analyzing." | [Upload CSV] [Add Manually] |
| Customers | "No customers yet. Upload data to connect feedback to revenue." | [Upload Customers] |
| Specs | "No specs yet. Ask the agent to create your first spec." | [Open Agent Chat] |
| Analytics | "Dashboards appear once you have feedback data." | [Upload Feedback] |

---

## Elasticsearch Indexes

| Index | Purpose | Created When |
|-------|---------|-------------|
| {org_id}-feedback | Feedback items with embeddings | First feedback upload |
| {org_id}-customers | Customer profiles | First customer upload |
| {org_id}-product-context | Product wizard data (all 8 sections) | Product wizard save |
| {org_id}-specs | Generated spec documents | First spec generation |

---

## Responsive Behavior

| Breakpoint | Behavior |
|-----------|----------|
| Desktop (>1200px) | Full sidebar + content + agent panel visible |
| Tablet (768-1200px) | Sidebar collapses to icons. Agent overlays content. |
| Mobile (<768px) | Hamburger menu. Agent full-screen overlay. Not optimized. |

---

## Feedback Sources Summary

| Source | Type | Now | Future |
|--------|------|-----|--------|
| App Store Reviews | External | CSV / Manual | Connector |
| G2 / Capterra | External | CSV / Manual | Connector |
| Support Tickets | External | CSV / Manual | Zendesk, Intercom |
| NPS / CSAT Surveys | External | CSV / Manual | Connector |
| Customer Emails | External | CSV / Manual | Connector |
| Sales Call Notes | Internal+External | CSV / Manual | CRM |
| Slack Messages | Internal | CSV / Manual / Connector | Available |
| Internal Team Feedback | Internal | CSV / Manual | Slack |
| User Interviews | Research | CSV / Manual | Connector |
| Bug Reports | Technical | CSV / Manual | Jira, Linear |
| Community / Discord | Community | CSV / Manual | Connector |

---

## Key Interactions Summary

| Action | Result |
|--------|--------|
| Click feedback item | Slide-out detail panel |
| Click customer row | Full customer profile page |
| Click "Investigate" | Agent chat with pre-filled query |
| Click "Generate Spec" | Agent generates 4 docs, saves to Specs |
| Click "View Specs" in agent | Navigate to Specs page |
| Click "Open in Kibana" | New tab with Kibana |
| Click product area on chart | Feedback page filtered |
| Click sentiment segment | Feedback page filtered |
| Click customer name anywhere | Customer profile page |
| Click feedback citation in spec | Feedback detail |
| Upload CSV | Column mapping → preview → import |
| Save product wizard step | Agent system prompt auto-updates |
| Toggle theme | Instant dark/light switch, saved |
| Customize dashboard | Show/hide widgets, saved |
