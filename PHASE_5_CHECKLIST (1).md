# Phase 5 Checklist — Agent + Tools

> Walk through EVERY item below after Cursor finishes Phase 5.
> You need: data from Phase 3 (feedback + customers), product wizard filled from Phase 2.
> You need: ANTHROPIC_API_KEY in your .env file with a valid Claude API key.
> This phase is conversational — many tests require reading agent responses and judging quality.

---

## Pre-Check: Phases 1-4 Still Work

- [ ] `docker compose up` starts without errors
- [ ] Log in → dashboard
- [ ] Feedback page: search works, filters work, detail slide-out works
- [ ] Customer page: list works, profile page works, sentiment chart works
- [ ] Settings > Product Wizard → data intact
- [ ] Dark/light theme works

---

## Pre-Check: Environment

- [ ] `.env` has `ANTHROPIC_API_KEY=sk-ant-...` (valid key)
- [ ] `.env` has `AGENT_MODEL=claude-sonnet-4-20250514` (or whichever model)
- [ ] `anthropic` package in requirements.txt
- [ ] Backend starts without import errors for anthropic

---

## A. Chat Panel UI

### A1. Open/Close
- [ ] Click agent chat bubble (bottom-right) → panel slides open from right
- [ ] Panel is ~400px wide
- [ ] Panel does NOT overlap sidebar
- [ ] Click minimize button → panel closes back to bubble
- [ ] Click bubble again → panel reopens
- [ ] Smooth animation on open/close (not instant jump)

### A2. Header
- [ ] Shows "Context Engine Agent" with bot icon
- [ ] Minimize button visible
- [ ] "New conversation" button visible
- [ ] History dropdown / button visible

### A3. Empty State (no messages yet)
- [ ] 6 suggested prompt chips visible:
  - [ ] "What's happening with checkout this week?"
  - [ ] "What should we prioritize this quarter?"
  - [ ] "Show me feedback from enterprise customers"
  - [ ] "Compare pricing sentiment: enterprise vs SMB"
  - [ ] "Generate specs for [top issue]"
  - [ ] "Which customers are at risk?"
- [ ] Clicking a chip sends that message

### A4. Input Area
- [ ] Text input with placeholder: "Ask me anything about your feedback..."
- [ ] Send button visible
- [ ] Press Enter → sends message
- [ ] Press Shift+Enter → inserts newline (doesn't send)
- [ ] Input clears after sending

### A5. Message Display
- [ ] User messages: right-aligned, accent color bubble
- [ ] Agent messages: left-aligned, different background
- [ ] Agent messages render markdown: **bold**, lists, tables, code blocks
- [ ] Messages scroll automatically as new ones appear
- [ ] Can scroll up to see older messages

---

## B. Tool 1: search_feedback

### B1. Basic Search
- [ ] Type: "Show me feedback about checkout"
- [ ] Agent responds with feedback items about checkout
- [ ] Response includes specific count ("Found 8 feedback items about checkout")
- [ ] Response includes actual feedback quotes/summaries
- [ ] Tool indicator shown: "🔍 Searching feedback..." (or similar)

### B2. Filtered Search
- [ ] Type: "What are enterprise customers saying about pricing?"
- [ ] Agent uses search_feedback with segment filter
- [ ] Response shows only enterprise feedback about pricing
- [ ] Includes customer names and sentiment

### B3. Source-Specific Search
- [ ] Type: "Show me recent support tickets"
- [ ] Agent filters by source = support_ticket
- [ ] Results are support tickets

---

## C. Tool 2: trend_analysis

### C1. General Trend
- [ ] Type: "Is checkout getting worse?"
- [ ] Agent uses trend_analysis tool
- [ ] Response includes: current vs previous period comparison
- [ ] Mentions volume change ("Checkout feedback increased 30%")
- [ ] Mentions sentiment shift ("Sentiment dropped from -0.4 to -0.6")
- [ ] Tool indicator: "📊 Analyzing trends..."

### C2. Specific Period
- [ ] Type: "What are the trends in the last 7 days?"
- [ ] Agent analyzes last 7 days vs previous 7 days
- [ ] Shows areas with biggest changes

### C3. Area-Specific
- [ ] Type: "How is dashboard feedback trending this month?"
- [ ] Agent focuses on "dashboard" product area
- [ ] Compares current month to previous month

---

## D. Tool 3: top_issues

### D1. General Issues
- [ ] Type: "What are the top issues right now?"
- [ ] Agent uses top_issues tool
- [ ] Response lists ranked issues (1, 2, 3...)
- [ ] Each issue includes:
  - [ ] Issue title/name
  - [ ] Feedback count
  - [ ] Severity (critical/emerging/stable)
  - [ ] Affected customers count
  - [ ] ARR impact (dollar amount)
- [ ] Issues are ranked by impact (not just volume)

### D2. Area-Specific Issues
- [ ] Type: "What are the biggest issues in checkout?"
- [ ] Agent filters top_issues by checkout area
- [ ] Only checkout-related issues shown

### D3. Goal Connection
- [ ] If a top issue relates to a business goal from wizard:
- [ ] Agent mentions: "This relates to your Q1 goal: Reduce checkout abandonment"

---

## E. Tool 4: find_similar

- [ ] Type: "Find feedback similar to 'the checkout keeps losing my cart'"
- [ ] Agent uses find_similar with the provided text
- [ ] Returns 3-5 similar feedback items
- [ ] Items are semantically related (not just keyword match)
- [ ] Each similar item shows text, sentiment, source

---

## F. Tool 5: customer_lookup

### F1. By Name
- [ ] Type: "Tell me about TechFlow Inc"
- [ ] Agent uses customer_lookup tool
- [ ] Response includes:
  - [ ] Company name, segment, plan
  - [ ] MRR / ARR (actual dollar amounts)
  - [ ] Health score
  - [ ] Account manager
  - [ ] Renewal date (with urgency if near)
  - [ ] Feedback count + average sentiment
  - [ ] Recent feedback items (quotes)

### F2. Unknown Customer
- [ ] Type: "What's going on with XyzNonExistent Corp?"
- [ ] Agent responds: "I couldn't find a customer named XyzNonExistent Corp" (not crash)

### F3. Risk Assessment
- [ ] Type: "Which customers are at risk?"
- [ ] Agent looks up customers with low health or negative feedback
- [ ] Mentions specific names, ARR, and why they're at risk

---

## G. Tool 6: compare_segments

- [ ] Type: "Compare enterprise vs SMB feedback"
- [ ] Agent uses compare_segments tool
- [ ] Response shows side-by-side comparison:
  - [ ] Feedback count per segment
  - [ ] Average sentiment per segment
  - [ ] Top product areas each segment cares about
- [ ] Clear which segment is happier/unhappier

### G2. Specific Area
- [ ] Type: "Compare how enterprise and SMB feel about checkout"
- [ ] Agent filters comparison to checkout area
- [ ] Shows checkout-specific comparison

---

## H. Tool 7: generate_spec_prep

- [ ] Type: "Prepare specs for the checkout issue"
- [ ] Agent uses generate_spec_prep tool
- [ ] Response includes comprehensive brief:
  - [ ] Topic name
  - [ ] Feedback count analyzed
  - [ ] Customers affected + total ARR
  - [ ] Top feedback quotes
  - [ ] Sentiment summary + trend
  - [ ] Related business goals (from wizard)
  - [ ] Relevant roadmap items (from wizard)
  - [ ] Recommended team (from wizard)
  - [ ] Competitor context (from wizard)
- [ ] Agent says something like "Data gathered. Full spec generation coming in the next phase."
- [ ] Does NOT generate 4 spec documents yet (that's Phase 6)

---

## I. System Prompt / Product Context

### I1. Context Awareness
- [ ] Type: "What product areas do we have?"
- [ ] Agent lists areas from product wizard (not generic guesses)
- [ ] Type: "What are our Q1 goals?"
- [ ] Agent lists goals from wizard Step 3
- [ ] Type: "Who are our competitors?"
- [ ] Agent lists competitors from wizard Step 5
- [ ] Type: "What team owns checkout?"
- [ ] Agent mentions the team from wizard Step 7

### I2. Context Used in Responses
- [ ] When discussing issues, agent connects to business goals
- [ ] When mentioning customers, agent includes segment + ARR
- [ ] When comparing, agent references competitor approaches
- [ ] Agent doesn't hallucinate product areas or goals not in wizard

---

## J. Conversation History

### J1. Within Session
- [ ] Ask: "What's happening with checkout?" → get response
- [ ] Follow up: "What about the trend?" → agent remembers context (knows you're still talking about checkout)
- [ ] Follow up: "Which customers are affected?" → still in context
- [ ] Agent doesn't repeat information already given

### J2. Conversation Continuity
- [ ] Send 5+ messages in a conversation
- [ ] All messages visible in chat panel (scrollable)
- [ ] Agent responses reference earlier parts of conversation appropriately

### J3. New Conversation
- [ ] Click "New conversation" button
- [ ] Chat clears
- [ ] Suggested prompts appear again
- [ ] Ask a question → agent starts fresh (no context from previous conversation)

### J4. Conversation History
- [ ] Click history dropdown
- [ ] Previous conversation(s) listed with title (auto-generated from first message)
- [ ] Click a past conversation → messages load
- [ ] Can continue the conversation or start a new one

---

## K. Context-Aware Pre-fills

### K1. From Feedback Page
- [ ] Go to Feedback page → click an item → detail slide-out opens
- [ ] Click "Ask agent" button in detail panel
- [ ] Chat panel opens
- [ ] Message pre-filled with something like "Analyze this feedback: [text preview]"
- [ ] Message auto-sends → agent responds about that specific feedback

### K2. From Customer Page
- [ ] Go to Customers → click a customer → profile page
- [ ] Click "Ask agent about this customer"
- [ ] Chat opens with "What's the situation with [company name]?"
- [ ] Agent responds with that customer's info

### K3. Placeholder Buttons (Dashboard)
- [ ] Dashboard "Investigate" and "Generate Spec" buttons exist (may be placeholder since dashboard widgets come in Phase 7)
- [ ] If dashboard has any clickable elements with agent actions → they open chat with pre-fill

---

## L. Response Quality

### L1. Data-Backed Answers
- [ ] Agent cites specific numbers (not vague)
  - [ ] ✅ "45 feedback items, average sentiment -0.72"
  - [ ] ❌ "There's some negative feedback about checkout"
- [ ] Agent mentions real customer names when relevant
- [ ] Agent includes ARR/MRR when discussing customer impact
- [ ] Agent connects insights to business goals

### L2. Markdown Rendering
- [ ] Bold text renders bold
- [ ] Lists render as lists
- [ ] Tables render as tables (if agent uses them)
- [ ] Code blocks render styled (if agent includes any)

### L3. Tool Transparency
- [ ] When agent uses a tool, PM sees what tool is being called
- [ ] "🔍 Searching feedback..." appears before results
- [ ] "📊 Analyzing trends..." appears before analysis
- [ ] Tool indicators disappear after results load

---

## M. Error Handling

### M1. Claude API Down
- [ ] Temporarily set `ANTHROPIC_API_KEY` to an invalid value
- [ ] Send a message → should see user-friendly error: "Agent is currently unavailable" or similar
- [ ] App doesn't crash
- [ ] Can restore valid key and agent works again (may need restart)

### M2. Empty Data
- [ ] If org has 0 feedback: agent should say "No feedback found" (not crash)
- [ ] If org has 0 customers: agent handles gracefully

### M3. Bad Input
- [ ] Send empty message → should be blocked or handled (not sent to API)
- [ ] Send very long message (1000+ chars) → agent processes (may truncate internally)

---

## N. API Verification (curl or devtools)

### N1. Chat Endpoint
- [ ] `POST /api/v1/agent/chat` with `{"message": "What are the top issues?"}` → 200
- [ ] Response has: conversation_id, response text, tools_used array
- [ ] Response has citations (if any feedback quoted)

### N2. Continuing Conversation
- [ ] Take the conversation_id from above
- [ ] `POST /api/v1/agent/chat` with `{"message": "Tell me more", "conversation_id": "..."}` → 200
- [ ] Agent has context from first message

### N3. Conversations List
- [ ] `GET /api/v1/agent/conversations` → 200, list of past conversations
- [ ] Each has: id, title, created_at, updated_at

### N4. Single Conversation
- [ ] `GET /api/v1/agent/conversations/{id}` → 200, full message history

### N5. Auth + Multi-Tenant
- [ ] Without JWT → 401
- [ ] Org A conversations not visible to Org B

---

## O. Elasticsearch Verification

- [ ] Open Kibana → check `{org_id}-conversations` index exists
- [ ] `GET {org_id}-conversations/_search` → see stored conversations
- [ ] Each conversation has: id, org_id, user_id, messages array, title, timestamps
- [ ] Messages array has: role (user/assistant), content, timestamp, tools_used

---

## P. Edge Cases

- [ ] Open chat on Feedback page → ask question → navigate to Customers page → chat stays open with history
- [ ] Open chat → minimize → navigate to different page → click bubble → chat reopens with history
- [ ] Two rapid messages → both process in order (no race condition)
- [ ] Agent uses multiple tools in one response (e.g., search + trend) → both shown
- [ ] Ask about a product area that doesn't exist → agent says "I don't see that area" (doesn't hallucinate)
- [ ] Ask in a different language → agent responds (may default to English, shouldn't crash)
- [ ] Very fast follow-up while agent is still responding → handled (queued or rejected, not crash)

---

## Q. UI/UX Quality

- [ ] Chat panel dark mode: all text readable, no white backgrounds
- [ ] Chat panel light mode: all text readable
- [ ] User message bubble clearly different from agent bubble
- [ ] Typing indicator animation smooth
- [ ] Long agent responses don't break layout
- [ ] Chat panel scrollable (doesn't overflow)
- [ ] Input area stays fixed at bottom
- [ ] Chat panel doesn't cover sidebar navigation
- [ ] On smaller screens: chat overlays content properly
- [ ] Agent chat bubble has unread indicator when new response arrives (if minimized)
- [ ] Suggested prompt chips visually appealing and clickable

---

## R. Backend Tests

- [ ] Run: `docker compose exec backend pytest`
- [ ] All Phase 1-4 tests still pass
- [ ] All Phase 5 tests pass:
  - [ ] test_agent_service.py (6 tests)
  - [ ] test_agent_tools.py (8 tests)
  - [ ] test_agent_routes.py (6 tests)
- [ ] No test failures

---

## S. Frontend Build

- [ ] No TypeScript errors: `docker compose exec frontend npx tsc --noEmit`
- [ ] No console errors during chat usage
- [ ] No React warnings

---

## Summary

| Section | Items | Status |
|---------|-------|--------|
| Pre-Check (Phases 1-4) | 6 | [ ] |
| Pre-Check (Environment) | 4 | [ ] |
| A. Chat Panel UI | 18 | [ ] |
| B. search_feedback Tool | 7 | [ ] |
| C. trend_analysis Tool | 7 | [ ] |
| D. top_issues Tool | 10 | [ ] |
| E. find_similar Tool | 5 | [ ] |
| F. customer_lookup Tool | 8 | [ ] |
| G. compare_segments Tool | 6 | [ ] |
| H. generate_spec_prep Tool | 11 | [ ] |
| I. System Prompt / Context | 8 | [ ] |
| J. Conversation History | 10 | [ ] |
| K. Context-Aware Pre-fills | 5 | [ ] |
| L. Response Quality | 8 | [ ] |
| M. Error Handling | 5 | [ ] |
| N. API Verification | 7 | [ ] |
| O. ES Verification | 3 | [ ] |
| P. Edge Cases | 7 | [ ] |
| Q. UI/UX Quality | 11 | [ ] |
| R. Backend Tests | 4 | [ ] |
| S. Frontend Build | 3 | [ ] |
| **TOTAL** | **~167** | |

**Phase 5 is DONE when every box above is checked.**
