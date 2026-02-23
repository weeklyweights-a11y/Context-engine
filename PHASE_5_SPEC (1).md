# Phase 5: Agent + Tools

> **Goal:** The agent chat panel becomes functional. An ES-powered conversational agent with 7 tools can search feedback, analyze trends, find issues, look up customers, compare segments, and prepare for spec generation. The agent knows the PM's full product context.
>
> **Done means:** PM opens chat, asks "What's happening with checkout this week?", and the agent searches feedback, analyzes sentiment trends, identifies top issues, and responds with data-backed insights. All 7 tools work. Product context is in the system prompt. Conversation history preserved within session.

---

## Context for the AI Agent

This is Phase 5 of 8. Phases 1-4 complete — auth, ES, product wizard, data ingestion, semantic search, feedback page, customer profiles.

This phase brings the intelligence layer. The agent is the PM's co-pilot. It can search, analyze, compare, and will generate specs in Phase 6.

Read `.cursorrules`. Read `UX.md` Flow 9 (Agent Chat).

---

## What You Are Building

| Component | What It Does |
|-----------|-------------|
| Agent backend | Conversational endpoint that routes to tools |
| 7 agent tools | search_feedback, trend_analysis, top_issues, find_similar, customer_lookup, compare_segments, generate_spec_prep |
| System prompt | Injected with full product context from wizard |
| React chat panel | Functional chat replacing Phase 1 placeholder |
| Conversation history | Within session, sent with each request |
| Context-aware pre-fills | Pre-fill chat from dashboard, feedback, customer pages |

---

## Agent Architecture

Two approaches (choose one based on what works best):

### Option A: Elasticsearch Agent Builder
- Use ES's built-in Agent Builder to define an agent with ES query tools
- Agent lives in Elastic Cloud, called via API
- Pro: Native ES integration, built-in tool calling
- Con: Less control over prompting, may have limitations

### Option B: Claude API as Agent Brain + ES Tools
- Use Claude (via Anthropic API) as the LLM
- Define tools as functions that execute ES queries
- Agent orchestration in FastAPI backend
- Pro: Full control, better reasoning, richer responses
- Con: Requires API key, external dependency

**Recommendation: Option B (Claude + ES Tools).** Better reasoning, full control over system prompt, richer tool definitions. ES Agent Builder is good for Kibana playground but limited for custom React UI.

**Implementation:**
- Backend receives user message + conversation history
- Builds system prompt with product context
- Sends to Claude API with tool definitions
- Claude decides which tools to call
- Backend executes tools (ES queries) and returns results to Claude
- Claude synthesizes and responds
- Backend returns response to frontend

---

## Environment Variables (add to .env)

```
ANTHROPIC_API_KEY=sk-ant-...
AGENT_MODEL=claude-sonnet-4-20250514
AGENT_MAX_TOKENS=4096
```

---

## Dependencies (add to requirements.txt)

| Package | Purpose |
|---------|---------|
| anthropic>=0.39.0 | Claude API client |

---

## Agent System Prompt

Built dynamically per org. Includes:

```
You are the Context Engine Agent — an AI assistant for Product Managers.

You help PMs understand their customer feedback, identify trends, prioritize issues, and generate engineering specs.

## Your Product Context

Product: {product_name}
Description: {description}
Industry: {industry}
Stage: {stage}

## Product Areas
{for each area: "- {name}: {description}"}

## Business Goals (Current Quarter)
{for each goal: "- [{priority}] {title}: {description} (linked to: {area})"}

## Customer Segments
{for each segment: "- {name}: {description} ({revenue_share}% of revenue)"}

## Pricing Tiers
{for each tier: "- {name}: ${price}/{period} ({segment})"}

## Competitors
{for each competitor: "- {name}: Strengths: {strengths}. Weaknesses: {weaknesses}. We differentiate: {differentiation}"}

## Roadmap
Existing: {for each: "- {name} ({status}) in {area}"}
Planned: {for each: "- {name} ({status}, target: {date}, {priority}) in {area}"}

## Teams
{for each team: "- {name} (lead: {lead}, owns: {areas}, {size} people, {slack_channel})"}

## Tech Stack
{for each tech: "- {category}: {technology} ({notes})"}

## Your Capabilities
You have access to tools that query the feedback database. Use them to give data-backed answers.
Always cite specific numbers (feedback count, sentiment scores, customer ARR).
When mentioning customers, include their segment and ARR.
When discussing issues, connect them to business goals and product areas.
When asked to generate specs, gather all relevant data first, then prepare a comprehensive brief.
```

---

## 7 Agent Tools

### Tool 1: search_feedback

Search feedback using semantic + keyword + filters.

```json
{
  "name": "search_feedback",
  "description": "Search customer feedback. Use for finding feedback about specific topics, features, or issues. Returns matching feedback items with text, sentiment, source, and customer info.",
  "parameters": {
    "query": "string - what to search for",
    "product_area": "string (optional) - filter by product area",
    "source": "string (optional) - filter by source type",
    "sentiment": "string (optional) - positive/negative/neutral",
    "customer_segment": "string (optional) - enterprise/smb/consumer/trial",
    "date_from": "string (optional) - ISO date",
    "date_to": "string (optional) - ISO date",
    "limit": "integer (optional, default 10) - max results"
  }
}
```

Implementation: Calls the search service from Phase 4.

### Tool 2: trend_analysis

Compare feedback metrics between two time periods.

```json
{
  "name": "trend_analysis",
  "description": "Analyze feedback trends over time. Compare current period to previous period. Shows volume changes, sentiment shifts, and emerging issues.",
  "parameters": {
    "product_area": "string (optional) - focus on specific area",
    "period": "string - '7d', '30d', '90d'",
    "metric": "string - 'volume', 'sentiment', 'both'"
  }
}
```

Implementation:
- Current period: last N days
- Previous period: N days before that
- ES date_histogram aggregation for volume
- ES avg aggregation on sentiment_score
- Calculate: % change in volume, sentiment shift, new vs declining topics

Returns:
```json
{
  "current_period": { "from": "...", "to": "...", "total_feedback": 120, "avg_sentiment": -0.23 },
  "previous_period": { "from": "...", "to": "...", "total_feedback": 98, "avg_sentiment": -0.18 },
  "volume_change": "+22.4%",
  "sentiment_change": "-0.05 (getting worse)",
  "top_areas_by_volume": [{"area": "checkout", "count": 45, "change": "+30%"}],
  "top_areas_by_negative_sentiment": [{"area": "checkout", "avg_sentiment": -0.6}]
}
```

### Tool 3: top_issues

Identify the most impactful issues across all feedback.

```json
{
  "name": "top_issues",
  "description": "Find the top issues from customer feedback ranked by impact. Impact considers: feedback volume, sentiment severity, customer revenue (ARR), growth rate, and alignment with business goals.",
  "parameters": {
    "limit": "integer (optional, default 5) - how many issues",
    "product_area": "string (optional) - filter by area",
    "period": "string (optional, default '30d') - time range"
  }
}
```

Implementation:
- Aggregate feedback by product_area + key terms
- For each cluster: count, avg sentiment, unique customers, total ARR of affected customers
- Score: volume × abs(sentiment) × customer_ARR_weight × growth_rate
- Return ranked list

Returns:
```json
{
  "issues": [
    {
      "rank": 1,
      "title": "Checkout: Form State Loss",
      "product_area": "checkout",
      "feedback_count": 45,
      "avg_sentiment": -0.72,
      "affected_customers": 23,
      "affected_arr": 450000,
      "growth_rate": "+30% vs prev period",
      "severity": "critical",
      "sample_feedback": ["Lost my cart 3 times...", "Form keeps resetting..."],
      "related_goal": "Reduce checkout abandonment by 30%"
    }
  ]
}
```

### Tool 4: find_similar

Find feedback similar to a given text or feedback ID.

```json
{
  "name": "find_similar",
  "description": "Find feedback items similar to a given text or feedback item. Uses semantic similarity.",
  "parameters": {
    "text": "string (optional) - text to find similar items for",
    "feedback_id": "string (optional) - ID of existing feedback item",
    "limit": "integer (optional, default 5)"
  }
}
```

Implementation: Calls the similar service from Phase 4.

### Tool 5: customer_lookup

Get customer profile and their feedback summary.

```json
{
  "name": "customer_lookup",
  "description": "Look up a customer by name or ID. Returns profile info, feedback summary, and sentiment trend.",
  "parameters": {
    "customer_name": "string (optional) - search by name",
    "customer_id": "string (optional) - exact ID lookup"
  }
}
```

Implementation:
- Search/get customer from customers index
- Get feedback count + avg sentiment for this customer
- Get recent feedback (last 5)
- Return combined profile

### Tool 6: compare_segments

Compare feedback across customer segments.

```json
{
  "name": "compare_segments",
  "description": "Compare feedback metrics between customer segments. Shows which segments are happiest/unhappiest, what each segment cares about.",
  "parameters": {
    "segments": "array of strings (optional, default all) - segments to compare",
    "product_area": "string (optional) - focus area",
    "period": "string (optional, default '30d')"
  }
}
```

Implementation:
- ES terms aggregation on customer_segment
- Sub-aggregations: count, avg sentiment, top product areas
- Return comparison table

### Tool 7: generate_spec_prep

Gather all data needed for spec generation (actual generation in Phase 6).

```json
{
  "name": "generate_spec_prep",
  "description": "Prepare data for generating engineering specs. Gathers all relevant feedback, customer impact, and context for a topic. In Phase 6 this will generate the full 4-doc spec.",
  "parameters": {
    "topic": "string - what the spec is about",
    "product_area": "string (optional) - primary area"
  }
}
```

Implementation:
- Search feedback for topic (semantic search)
- Get top issues related to topic
- Get affected customers + ARR
- Get product context (goals, roadmap, teams, competitors)
- Return comprehensive brief

Returns:
```json
{
  "topic": "checkout form state loss",
  "feedback_count": 45,
  "customers_affected": 23,
  "total_arr_affected": 450000,
  "top_feedback": [...5 most representative items...],
  "sentiment_summary": { "avg": -0.72, "trend": "worsening" },
  "related_goals": ["Reduce checkout abandonment by 30%"],
  "relevant_roadmap": ["Advanced Filtering planned for Q2"],
  "recommended_team": "Payments Team (Mike Rodriguez)",
  "competitor_context": "Mixpanel handles this by..."
}
```

Note: This tool prepares data but does NOT generate specs yet. Phase 6 will add the actual generation.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /agent/chat | Yes | Send message, get agent response |
| GET | /agent/conversations | Yes | List past conversations |
| GET | /agent/conversations/{id} | Yes | Get single conversation |

### POST /api/v1/agent/chat

Request:
```json
{
  "message": "What's happening with checkout this week?",
  "conversation_id": "conv_001 (optional, for continuing)",
  "context": {
    "page": "dashboard",
    "pre_fill": "Tell me about checkout issues"
  }
}
```

Response (streamed or full):
```json
{
  "data": {
    "conversation_id": "conv_001",
    "response": "Based on the last 7 days, checkout feedback has increased 30%...",
    "tools_used": ["search_feedback", "trend_analysis"],
    "citations": [
      { "feedback_id": "fb_001", "text": "Lost my cart 3 times..." }
    ]
  }
}
```

### Conversation Storage

Store conversations in ES index: `{org_id}-conversations`

| Field | ES Type |
|-------|---------|
| id | keyword |
| org_id | keyword |
| user_id | keyword |
| messages | nested (array of {role, content, timestamp, tools_used}) |
| created_at | date |
| updated_at | date |
| title | text (auto-generated from first message) |

---

## Services (Backend)

### services/agent_service.py
- `chat(org_id, user_id, message, conversation_id, context)` — Main agent function
- `build_system_prompt(org_id)` — Fetch product context, build prompt
- `execute_tool(org_id, tool_name, parameters)` — Route tool call to correct service
- `save_conversation(org_id, conversation_id, messages)` — Store in ES
- `get_conversations(org_id, user_id)` — List conversations
- `get_conversation(org_id, conversation_id)` — Get one conversation

### services/agent_tools.py
- `search_feedback_tool(org_id, params)` — Wraps search service
- `trend_analysis_tool(org_id, params)` — ES aggregations for trends
- `top_issues_tool(org_id, params)` — Aggregation + scoring
- `find_similar_tool(org_id, params)` — Wraps similar service
- `customer_lookup_tool(org_id, params)` — Customer + feedback summary
- `compare_segments_tool(org_id, params)` — Segment aggregations
- `generate_spec_prep_tool(org_id, params)` — Comprehensive data gathering

---

## Frontend

### Agent Chat Panel (Full Implementation)

Replace Phase 1 placeholder. See UX.md Flow 9 for full details.

**AgentChatPanel.tsx** (right sidebar, 400px)

Header:
- "Context Engine Agent" + bot icon
- Minimize button (→ bubble)
- New conversation button
- History dropdown (list past conversations)

Messages area:
- User messages: right-aligned, accent color bubble
- Agent messages: left-aligned, styled markdown
  - Support: bold, lists, code blocks, tables
  - Inline data: feedback counts, sentiment scores highlighted
  - Tool usage indicators: "Searching feedback..." → "Found 45 items"
  - Citations: feedback text quotes with clickable links
  - Action buttons within responses: [View in Feedback] [View Customer]

Input area:
- Text input: "Ask me anything about your feedback..."
- Send button + Enter key to send
- Shift+Enter for newline

When empty (no messages):
- 6 suggested prompt chips:
  - "What's happening with checkout this week?"
  - "What should we prioritize this quarter?"
  - "Show me feedback from enterprise customers"
  - "Compare pricing sentiment: enterprise vs SMB"
  - "Generate specs for [top issue]"
  - "Which customers are at risk?"

Loading state:
- Typing indicator while agent processes
- Tool usage shown: "🔍 Searching feedback..." → "📊 Analyzing trends..."

### Context-Aware Pre-fills

Wire up action buttons from other pages:

- Dashboard "Investigate" button → opens chat with "Tell me more about {issue}"
- Dashboard "Generate Spec" button → opens chat with "Generate specs for {issue}"
- Feedback detail "Ask agent" → opens chat with "Analyze this feedback: {text preview}"
- Customer profile "Ask agent" → opens chat with "What's the situation with {company}?"

Implementation:
- `useAgentChat` hook with `openWithMessage(message)` function
- Action buttons call this hook
- Chat panel opens and sends the pre-filled message automatically

### AgentChatBubble.tsx Update
- Now opens the real chat panel (not placeholder)
- Unread indicator (dot) when agent has new response
- Smooth animation open/close

---

## Testing

### test_agent_service.py
1. Build system prompt includes product context.
2. Build system prompt handles missing product context gracefully.
3. Execute tool routes to correct service.
4. Execute tool with invalid name → error.
5. Save conversation stores in ES.
6. Get conversations returns only current org's conversations.

### test_agent_tools.py
1. search_feedback_tool returns results from ES.
2. trend_analysis_tool returns period comparison.
3. top_issues_tool returns ranked issues with scores.
4. find_similar_tool returns similar items.
5. customer_lookup_tool returns profile + feedback summary.
6. compare_segments_tool returns segment comparison.
7. generate_spec_prep_tool returns comprehensive brief.
8. All tools filter by org_id.

### test_agent_routes.py
1. POST /agent/chat with message → 200 with response.
2. POST /agent/chat continues conversation with conversation_id.
3. GET /agent/conversations returns list.
4. GET /agent/conversations/{id} returns conversation.
5. All endpoints require auth.
6. All endpoints isolate by org_id.

---

## Non-Negotiable Rules

1. **Product context ALWAYS in system prompt.** Agent must know the PM's product at all times.
2. **Tools execute real ES queries.** No mocked or fake data.
3. **Conversation history sent with each request.** Agent remembers within session.
4. **org_id isolation on every tool.** Agent never sees another org's data.
5. **Tool usage shown to PM.** Don't hide what the agent is doing.
6. **Agent responses cite real data.** Feedback count, sentiment scores, customer names — always specific.
7. **Graceful degradation.** If Claude API is down, show error. Don't crash app.

---

## What NOT to Build

- Full spec generation (Phase 6 — generate_spec_prep gathers data, doesn't write specs)
- Dashboard widgets (Phase 7)
- Kibana dashboards (Phase 7)
- Slack connector (Phase 8)

---

## Acceptance Criteria

- [ ] PM opens agent chat and sees suggested prompts
- [ ] PM sends message, gets response from agent
- [ ] Agent uses search_feedback tool and returns relevant results
- [ ] Agent uses trend_analysis tool and reports changes
- [ ] Agent uses top_issues tool and ranks issues by impact
- [ ] Agent uses find_similar tool and finds related feedback
- [ ] Agent uses customer_lookup tool and returns profile + feedback
- [ ] Agent uses compare_segments tool and shows comparison
- [ ] Agent uses generate_spec_prep tool and gathers comprehensive data
- [ ] Agent system prompt includes full product context from wizard
- [ ] Agent responses include specific numbers (counts, sentiment, ARR)
- [ ] Tool usage indicators shown ("Searching feedback...")
- [ ] Conversation history preserved within session
- [ ] Past conversations listed in chat header dropdown
- [ ] Dashboard "Investigate" opens chat with pre-filled query
- [ ] Feedback "Ask agent" opens chat with context
- [ ] Customer "Ask agent" opens chat with context
- [ ] Chat panel minimizes to bubble
- [ ] Chat panel responsive (overlay on smaller screens)
- [ ] Claude API errors handled gracefully
- [ ] All data filtered by org_id
- [ ] All backend tests pass
- [ ] All previous phase tests still pass

---

## How to Give This to Cursor

> Read docs/PHASE_5_SPEC.md, PROJECT.md, and UX.md (Flow 9). This is Phase 5. The .cursorrules file applies. Create implementation plan, wait for approval.

---

## After Phase 5

Phase 6: Spec Generation. The generate_spec tool produces 4 full documents (PRD, Architecture, Rules, Plan), saved to ES, viewable in the Specs page.
