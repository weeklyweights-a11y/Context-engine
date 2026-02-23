# Phase 8: Polish + Ship

> **Goal:** Everything is finished, polished, and ready to demo or deploy. Settings complete. Slack connector. Responsive. Edge cases handled. README written. The product feels complete.
>
> **Done means:** A new user can clone the repo, docker compose up, sign up, go through onboarding, upload data, search, chat with the agent, generate specs, and monitor dashboards. Everything works end-to-end. README documents everything.

---

## Context for the AI Agent

This is Phase 8 of 8 — the final phase. Phases 1-7 complete. The product works but needs polish, missing settings, edge case handling, and documentation.

Read `.cursorrules`. Read `UX.md` Flow 8 (Settings), and review all empty states and responsive behavior.

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Settings > Connectors | Slack integration (OAuth, channel selection, auto-ingest) |
| Settings > Account | Full account management (name, password, delete) |
| Settings > Elasticsearch | Connection details, index stats, data management |
| Responsive behavior | Sidebar collapse, tablet support, basic mobile |
| Error handling polish | Every API error shows user-friendly message |
| Loading states polish | Every page/component has loading skeleton |
| Empty states polish | Every page has helpful empty state with CTA |
| README.md | Setup guide, screenshots, architecture overview |
| Demo script | Step-by-step demo walkthrough |
| End-to-end verification | Fresh install → full workflow |

---

## Settings > Connectors

### Slack Integration

**OAuth Flow:**
1. PM clicks "Connect Slack" → redirects to Slack authorization
2. PM approves → callback saves encrypted token
3. PM selects channels to monitor
4. Messages from selected channels auto-create feedback items

**Environment Variables (add to .env):**
```
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
SLACK_SIGNING_SECRET=
ENCRYPTION_KEY=generate-a-fernet-key
```

**Dependencies (add to requirements.txt):**
| Package | Purpose |
|---------|---------|
| slack-bolt>=1.18.0 | Slack OAuth + Events API |
| slack-sdk>=3.26.0 | Slack API client |
| cryptography>=41.0.0 | Fernet encryption for tokens |

**Elasticsearch Index: `slack-connections`**

| Field | ES Type | Purpose |
|-------|---------|---------|
| id | keyword | UUID |
| org_id | keyword | One per org (unique) |
| team_id | keyword | Slack workspace ID |
| team_name | keyword | Workspace name |
| access_token | keyword | Encrypted (Fernet) |
| bot_user_id | keyword | Bot user ID |
| incoming_channels | keyword (array) | Channel IDs to monitor |
| is_active | boolean | Toggle on/off |
| created_at | date | |
| updated_at | date | |

**API Endpoints:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /slack/install | Yes | Redirect to Slack OAuth |
| GET | /slack/oauth/callback | No | Slack redirect callback |
| GET | /slack/channels | Yes | List workspace channels |
| POST | /slack/channels | Yes | Set monitored channels |
| POST | /slack/events | No | Slack webhook (signed) |
| GET | /slack/status | Yes | Connection status |
| DELETE | /slack/disconnect | Yes | Remove connection |

**Slack event processing:**
- Verify signing secret on every event
- Ignore bot messages, edits, deletes
- Async processing (no Celery needed)
- Create feedback item: source="slack_message", ingestion_method="slack_connector"
- Deduplicate by channel:timestamp combo
- Fetch user profile for author_name/email
- Auto-analyze sentiment (same as CSV import)

**Services:**
- `services/slack_service.py` — OAuth, channels, event processing
- `services/encryption_service.py` — Fernet encrypt/decrypt

**Frontend: Settings > Connectors tab**
- If not connected: "Connect Slack" button with Slack icon
- If connected: workspace name, channel list with toggles, "Disconnect" button
- Future connectors: Zendesk, Intercom, Jira, Linear shown as "Coming Soon" cards with "Notify me" buttons

---

## Settings > Account

**SettingsAccountTab.tsx**

- Email display (read-only)
- Full name — editable, save button
- Change password — current password + new password + confirm
- Organization name — editable
- Theme toggle (dark/light) — already exists, include here
- Dashboard default period preference
- "Delete account" — destructive, requires typing "DELETE" to confirm

**API Endpoints:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| PUT | /auth/profile | Yes | Update name |
| PUT | /auth/password | Yes | Change password |
| PUT | /auth/org | Yes | Update org name |
| DELETE | /auth/account | Yes | Delete account + all org data |

**Delete account:** Removes user, org, and ALL org indexes ({org_id}-feedback, customers, product-context, specs, conversations). Requires confirmation body `{"confirm": "DELETE"}`.

---

## Settings > Elasticsearch

**SettingsElasticsearchTab.tsx**

- Connection status: green/red indicator
- Cluster name + version (from /health)
- **Index stats table:**

| Index | Documents | Size |
|-------|-----------|------|
| {org_id}-feedback | 847 | 12.4 MB |
| {org_id}-customers | 156 | 1.2 MB |
| {org_id}-product-context | 8 | 0.1 MB |
| {org_id}-specs | 12 | 2.3 MB |
| {org_id}-conversations | 28 | 0.5 MB |

- "Re-index all" button
- "Clear all data" button — destructive, requires typing "DELETE"
- Kibana URL link → opens in new tab

**API Endpoints:**
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /admin/index-stats | Yes | Index document counts + sizes |
| POST | /admin/reindex | Yes | Trigger re-index |
| DELETE | /admin/clear-data | Yes | Delete all org data |

---

## Responsive Behavior

### Desktop (>1200px)
- Full sidebar (240px) + content + agent panel can coexist
- Dashboard: 2-column widget grid

### Tablet (768-1200px)
- Sidebar collapses to icon-only mode (64px)
- Tooltip on hover for nav items
- Agent chat overlays content
- Dashboard: single column
- Tables: horizontal scroll if needed

### Mobile (<768px)
- Hamburger menu replaces sidebar
- Agent chat: full-screen overlay
- Dashboard: single column, simplified cards
- Tables: card view instead of rows
- Functional but not fully optimized

**Implementation:**
- Tailwind responsive classes (md:, lg: breakpoints)
- `useSidebar` hook for collapse state
- `useMediaQuery` hook for breakpoint detection
- Collapse state saved to localStorage

---

## Error Handling Polish

Audit ALL pages for user-friendly error messages:

| Error | User Sees |
|-------|-----------|
| Network error | "Unable to connect. Check your internet connection." + retry |
| 401 | Redirect to /login |
| 403 | "You don't have permission to do this." |
| 404 | "This item doesn't exist or was removed." |
| 422 | Field-specific error messages below inputs |
| 429 | "Too many requests. Please wait a moment." |
| 500 | "Something went wrong. Please try again." |
| ES down | "Database connection issue. Check Settings > Elasticsearch." |

**Toast component:** Success (green, 3s), Error (red, persistent), Info (blue, 5s).

---

## Loading States Polish

Every page must have loading skeletons:
- Dashboard: 9 skeleton cards/charts
- Feedback list: skeleton rows
- Feedback detail: skeleton content block
- Customer list: skeleton table rows
- Customer profile: skeleton header + cards
- Specs list: skeleton cards
- Spec detail: skeleton content
- Agent chat: typing indicator dots
- Settings tabs: skeleton forms

Create `Skeleton.tsx` component with variants: card, row, text, chart.

---

## Empty States Polish

Verify every page per UX.md:
| Page | Message | CTA |
|------|---------|-----|
| Dashboard | "No data yet. Set up your product and upload feedback." | [Start Product Wizard] [Upload Feedback] |
| Feedback | "No feedback yet. Import data to start analyzing." | [Upload CSV] [Add Manually] |
| Customers | "No customers yet. Upload data to connect feedback to revenue." | [Upload Customers] |
| Specs | "No specs yet. Ask the agent to create your first spec." | [Open Agent Chat] |
| Analytics | "Dashboards appear once you have feedback data." | [Upload Feedback] |

---

## README.md

```markdown
# Context Engine v2

Feedback intelligence platform for Product Managers. Powered by Elasticsearch.

## What It Does
- Import customer feedback from 11 sources (CSV, manual, Slack)
- Semantic search across all feedback (powered by ELSER)
- AI agent analyzes trends, identifies issues, compares segments
- Generate 4-doc engineering specs (PRD, Architecture, Rules, Plan) grounded in real data
- Dashboard with 9 widgets for daily monitoring
- Customer profiles with revenue data and sentiment trends
- Deep analytics via embedded Kibana dashboards

## Quick Start
1. Clone: `git clone ...`
2. Configure: `cp .env.example .env` → fill in ES + Anthropic credentials
3. Start: `docker compose up`
4. Open: http://localhost:3000
5. Sign up → Product Wizard → Upload data → Search → Chat → Generate specs

## Architecture
React (Vite + TypeScript + Tailwind) → FastAPI (Python 3.11) → Elasticsearch 8.x (Elastic Cloud)
AI: Claude API (Anthropic) + ELSER (Elastic)

## Features
[Feature list with brief descriptions]

## Development
[How to run tests, environment setup]

## Project Structure
[File tree overview]

## License
MIT
```

---

## Demo Script (docs/demo_script.md)

8-minute walkthrough:
1. Problem statement (30s)
2. Sign up + product wizard (1 min)
3. Upload feedback CSV (1 min)
4. Semantic search + filters (1 min)
5. Agent chat — trends, issues, customers (2 min)
6. Spec generation → 4-tab viewer (1 min)
7. Dashboard overview (1 min)
8. Wrap up (30s)

---

## Testing

### test_slack_service.py
1. OAuth install URL generated correctly.
2. Callback saves encrypted token.
3. List channels returns workspace channels.
4. Set channels updates connection.
5. Event processing creates feedback item.
6. Duplicate events deduplicated.
7. Bot messages ignored.
8. Disconnect removes connection.

### test_account_routes.py
1. PUT /auth/profile updates name.
2. PUT /auth/password with correct current → updated.
3. PUT /auth/password with wrong current → 401.
4. PUT /auth/org updates org name.
5. DELETE /auth/account with confirm → all data removed.
6. DELETE /auth/account without confirm → 400.

### test_admin_routes.py
1. GET /admin/index-stats returns index counts.
2. POST /admin/reindex triggers re-index.
3. DELETE /admin/clear-data removes all org data.
4. All require auth + isolate by org_id.

---

## Non-Negotiable Rules

1. **Slack tokens encrypted at rest.** Never store plaintext OAuth tokens.
2. **Delete account removes EVERYTHING.** All indexes for that org.
3. **Loading skeletons on EVERY page.** No blank flashes.
4. **Empty states on EVERY page.** Helpful message + CTA.
5. **Error toasts on EVERY API failure.** User-friendly, not technical.
6. **README enables zero-knowledge setup.** Clone → compose up → working.
7. **Demo script is rehearsed.** Every step works smoothly.

---

## Acceptance Criteria

- [ ] Settings > Connectors: Slack OAuth flow works
- [ ] Slack: channels listed, selectable, toggleable
- [ ] Slack: messages from monitored channels appear as feedback
- [ ] Slack: disconnect removes integration
- [ ] Settings > Account: update name works
- [ ] Settings > Account: change password works
- [ ] Settings > Account: update org name works
- [ ] Settings > Account: delete account removes all data
- [ ] Settings > Elasticsearch: connection status shown
- [ ] Settings > Elasticsearch: index stats table accurate
- [ ] Settings > Elasticsearch: clear data works (with DELETE confirmation)
- [ ] Sidebar collapses to icons on tablet
- [ ] Chat overlays on tablet/mobile
- [ ] Dashboard single-column on tablet/mobile
- [ ] Hamburger menu on mobile
- [ ] Error toasts on API failures (all pages audited)
- [ ] Loading skeletons on all pages
- [ ] Empty states on all pages (with correct CTAs)
- [ ] README.md written with setup instructions
- [ ] Demo script written and tested
- [ ] End-to-end: fresh install → signup → onboard → upload → search → chat → specs → dashboard
- [ ] All Phase 8 tests pass
- [ ] ALL previous phase tests still pass

---

## How to Give This to Cursor

> Read docs/PHASE_8_SPEC.md, PROJECT.md, and UX.md (Flow 8, responsive behavior). This is the final phase. Create implementation plan, wait for approval.

---

## After Phase 8

**The product is feature-complete for v2.** The full pipeline works:

```
Onboarding → Product Wizard → Upload Feedback + Customers → Semantic Search →
AI Agent (7 tools) → Spec Generation (4 docs) → Dashboard (9 widgets) → Analytics (Kibana)
```
