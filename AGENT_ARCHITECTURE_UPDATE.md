# Agent Architecture Update: Elastic Agent Builder (replaces Claude API)

> This document explains what changes in Phases 5, 6, and 8 when using Elasticsearch Agent Builder instead of Claude API.
> Give this to Cursor alongside the phase spec so it knows the architecture.

---

## What Changed and Why

**Before:** Claude API as the LLM brain + custom Python tool functions that execute ES queries.

**Now:** Elastic Agent Builder — ES's built-in agent framework. The agent, tools, and LLM orchestration all live inside Elasticsearch. Your FastAPI backend calls the Kibana Agent Builder API to chat.

**Why:** This is for an Elasticsearch hackathon. Using their native agent framework showcases the ES ecosystem better and eliminates external LLM dependencies.

---

## How Elastic Agent Builder Works

### Three APIs

| API | Endpoint | What It Does |
|-----|----------|-------------|
| **Tools API** | `POST /api/agent_builder/tools` | Register custom ES|QL query tools |
| **Agents API** | `POST /api/agent_builder/agents` | Create a custom agent with system prompt + tool assignments |
| **Converse API** | `POST /api/agent_builder/converse` | Send a message, get a response (sync) |
| **Converse Async** | `POST /api/agent_builder/converse/async` | Send a message, get streamed response |

All APIs go through **Kibana URL** (not Elasticsearch directly), authenticated with an API key.

### Flow

```
PM types: "What's happening with checkout this week?"
     ↓
FastAPI backend → POST {KIBANA_URL}/api/agent_builder/converse
                  { "input": "What's happening with checkout?",
                    "agent_id": "context-engine-agent",
                    "conversation_id": "conv_001" }
     ↓
Agent Builder (inside ES):
  1. Agent reads its custom instructions (system prompt)
  2. Agent decides which tools to call
  3. Runs ES|QL tools against your indexes
  4. Synthesizes results into natural language response
     ↓
FastAPI receives response → sends to React frontend
```

### Key Difference from Claude Approach

| Aspect | Claude API (old) | Agent Builder (new) |
|--------|-----------------|-------------------|
| LLM | Claude (external) | ES-configured connector (OpenAI, Anthropic, or local) |
| Tools | Python functions calling ES client | ES|QL queries registered as Agent Builder tools |
| Orchestration | Custom Python loop in FastAPI | Agent Builder handles tool selection + execution |
| Conversation history | Manual (stored in ES, sent with each request) | Agent Builder manages conversations natively |
| System prompt | Built dynamically in Python | Set in agent configuration via API |
| Where tools run | In your FastAPI process | Inside Elasticsearch/Kibana |

---

## Environment Variables (replaces ANTHROPIC_API_KEY)

```env
# Elastic Agent Builder
KIBANA_URL=https://your-deployment.kb.us-east-1.aws.elastic-cloud.com
KIBANA_API_KEY=your-kibana-api-key
AGENT_ID=context-engine-agent
```

**Note:** Agent Builder still needs an LLM connector configured in Kibana (OpenAI, Azure OpenAI, Anthropic, Bedrock, or local). This is configured in Kibana UI under Stack Management > Connectors. The agent uses whatever LLM connector you set up — but it's all managed through ES, not your app code.

---

## Phase 5 Changes: Agent + Tools

### 7 Custom ES|QL Tools to Register

Register these via the Agent Builder Tools API during setup/deployment:

#### Tool 1: search_feedback

```json
{
  "id": "context_engine.search_feedback",
  "type": "esql",
  "description": "Search customer feedback by topic, product area, source, sentiment, segment, or date range. Use this when the user asks about feedback on a specific topic or wants to find what customers are saying.",
  "configuration": {
    "query": "FROM {org_id}-feedback | WHERE MATCH(text, ?search_query) | STATS count = COUNT(*), avg_sentiment = AVG(sentiment_score) BY product_area | SORT count DESC | LIMIT ?result_limit"
  },
  "params": {
    "search_query": { "type": "keyword", "description": "What to search for in feedback text" },
    "result_limit": { "type": "integer", "description": "Max results to return", "default": 10 }
  }
}
```

#### Tool 2: trend_analysis

```json
{
  "id": "context_engine.trend_analysis",
  "type": "esql",
  "description": "Analyze feedback trends over time. Compare current period volume and sentiment to previous period. Use when user asks about trends, changes, or whether things are getting better/worse.",
  "configuration": {
    "query": "FROM {org_id}-feedback | WHERE created_at >= NOW() - ?period | STATS feedback_count = COUNT(*), avg_sentiment = AVG(sentiment_score), negative_count = COUNT_IF(sentiment == \"negative\") BY product_area | SORT feedback_count DESC | LIMIT 20"
  },
  "params": {
    "period": { "type": "keyword", "description": "Time period: 7 days, 30 days, 90 days", "default": "30 days" }
  }
}
```

#### Tool 3: top_issues

```json
{
  "id": "context_engine.top_issues",
  "type": "esql",
  "description": "Find the most impactful issues from customer feedback, ranked by volume and severity. Use when user asks about top problems, priorities, or what to fix first.",
  "configuration": {
    "query": "FROM {org_id}-feedback | WHERE sentiment == \"negative\" AND created_at >= NOW() - ?period | STATS issue_count = COUNT(*), avg_sentiment = AVG(sentiment_score), unique_customers = COUNT_DISTINCT(customer_name) BY product_area | SORT issue_count DESC | LIMIT ?limit"
  },
  "params": {
    "period": { "type": "keyword", "default": "30 days" },
    "limit": { "type": "integer", "default": 5 }
  }
}
```

#### Tool 4: find_similar

```json
{
  "id": "context_engine.find_similar",
  "type": "esql",
  "description": "Find feedback items similar to a given text using semantic search. Use when user wants to find related feedback or see patterns.",
  "configuration": {
    "query": "FROM {org_id}-feedback METADATA _score | WHERE MATCH(text, ?search_text) | KEEP text, sentiment, sentiment_score, product_area, customer_name, created_at, _score | SORT _score DESC | LIMIT 5"
  },
  "params": {
    "search_text": { "type": "keyword", "description": "Text to find similar feedback for" }
  }
}
```

#### Tool 5: customer_lookup

```json
{
  "id": "context_engine.customer_lookup",
  "type": "esql",
  "description": "Look up a customer profile and their feedback summary. Use when user asks about a specific company or customer.",
  "configuration": {
    "query": "FROM {org_id}-customers | WHERE company_name LIKE ?customer_name | KEEP company_name, segment, plan, mrr, arr, health_score, account_manager, renewal_date, industry, employee_count | LIMIT 5"
  },
  "params": {
    "customer_name": { "type": "keyword", "description": "Customer/company name to look up" }
  }
}
```

#### Tool 6: compare_segments

```json
{
  "id": "context_engine.compare_segments",
  "type": "esql",
  "description": "Compare feedback metrics between customer segments (enterprise, SMB, trial, etc). Use when user asks about segment differences or which segment is happiest/unhappiest.",
  "configuration": {
    "query": "FROM {org_id}-feedback | WHERE created_at >= NOW() - ?period | STATS feedback_count = COUNT(*), avg_sentiment = AVG(sentiment_score), negative_pct = COUNT_IF(sentiment == \"negative\") * 100.0 / COUNT(*) BY customer_segment | SORT feedback_count DESC"
  },
  "params": {
    "period": { "type": "keyword", "default": "30 days" }
  }
}
```

#### Tool 7: generate_spec_prep

```json
{
  "id": "context_engine.generate_spec_prep",
  "type": "esql",
  "description": "Gather all data needed to generate engineering specs for a topic. Returns feedback summary, affected customers, and impact. Use when user asks to prepare or generate specs.",
  "configuration": {
    "query": "FROM {org_id}-feedback | WHERE MATCH(text, ?topic) | STATS total_feedback = COUNT(*), avg_sentiment = AVG(sentiment_score), unique_customers = COUNT_DISTINCT(customer_name), sources = VALUES(source) BY product_area | SORT total_feedback DESC | LIMIT 10"
  },
  "params": {
    "topic": { "type": "keyword", "description": "The topic/issue to gather spec data for" }
  }
}
```

**Important:** The `{org_id}` in index names needs to be handled. Two approaches:
1. **Per-org tools:** Register tools per org with the actual index name baked in (simpler, works for hackathon)
2. **Index pattern:** Use a wildcard index pattern and add org_id filter in the query

For hackathon: approach 1 is faster. Register tools when the org first uses the agent.

### Custom Agent Registration

```json
POST /api/agent_builder/agents
{
  "id": "context-engine-agent",
  "display_name": "Context Engine Agent",
  "description": "AI assistant for Product Managers. Analyzes customer feedback, identifies trends, and helps generate engineering specs.",
  "configuration": {
    "instructions": "You are the Context Engine Agent — an AI assistant for Product Managers.\n\nYou help PMs understand their customer feedback, identify trends, prioritize issues, and generate engineering specs.\n\n## Product Context\n\nProduct: {product_name}\nDescription: {description}\nIndustry: {industry}\nStage: {stage}\n\n## Product Areas\n{areas_list}\n\n## Business Goals\n{goals_list}\n\n## Customer Segments\n{segments_list}\n\n## Competitors\n{competitors_list}\n\n## Teams\n{teams_list}\n\n## Rules\n- Always cite specific numbers (feedback count, sentiment scores, ARR)\n- When mentioning customers, include segment and ARR\n- Connect issues to business goals and product areas\n- When asked to generate specs, gather all relevant data first",
    "tools": [
      "context_engine.search_feedback",
      "context_engine.trend_analysis",
      "context_engine.top_issues",
      "context_engine.find_similar",
      "context_engine.customer_lookup",
      "context_engine.compare_segments",
      "context_engine.generate_spec_prep"
    ]
  }
}
```

### Backend Service Changes

**services/agent_service.py** — REPLACES the Claude-based approach:

```python
import httpx

class AgentService:
    def __init__(self, kibana_url, api_key, agent_id):
        self.kibana_url = kibana_url
        self.api_key = api_key
        self.agent_id = agent_id

    async def chat(self, message: str, conversation_id: str = None):
        """Send message to Agent Builder, get response."""
        payload = {
            "input": message,
            "agent_id": self.agent_id,
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.kibana_url}/api/agent_builder/converse",
                json=payload,
                headers={
                    "Authorization": f"ApiKey {self.api_key}",
                    "kbn-xsrf": "true",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            return response.json()

    async def register_tools(self, org_id: str):
        """Register org-specific ES|QL tools in Agent Builder."""
        # Called once per org, registers 7 tools with org_id baked into index names
        ...

    async def register_agent(self, org_id: str, product_context: dict):
        """Register/update custom agent with product context in system prompt."""
        # Builds instructions from product wizard data
        ...
```

### What This Means for the Frontend

**No change.** The React chat panel still calls your FastAPI backend:

```
React → POST /api/v1/agent/chat → FastAPI → POST {KIBANA_URL}/api/agent_builder/converse → response → React
```

FastAPI is a thin proxy. The intelligence is in Agent Builder.

### Conversation History

**Agent Builder manages this natively.** When you pass `conversation_id` to the converse API, it maintains context automatically. No need to store/replay message history in your own ES index.

You still want to store conversations in `{org_id}-conversations` for the UI (listing past conversations), but you don't need to replay them with each request.

---

## Phase 6 Changes: Spec Generation

**This is the one place you still might need a direct LLM call.** Agent Builder is great for conversational Q&A, but generating 4 long-form documents (PRD, Architecture, Rules, Plan) is a different pattern.

Two approaches:

### Approach A: Use Agent Builder for spec generation too
- Create a `generate_full_spec` tool that gathers data
- The agent's response IS the spec content
- Limitation: single response = single document, hard to get 4 separate docs

### Approach B: Hybrid — Agent Builder for chat, ES Inference API for spec generation
- Phase 5 (chat) → Agent Builder
- Phase 6 (spec generation) → Use ES Inference API to call an LLM for long-form generation
- ES Inference API: `POST /_inference/completion/{inference_id}`
- Still 100% within the Elastic ecosystem
- Better for generating structured, multi-document output

**Recommendation for hackathon: Approach B.** Use Agent Builder for chat, ES Inference API for spec generation. Both are Elastic-native. Judges will appreciate that you're using multiple Elastic AI capabilities.

### ES Inference API for Spec Generation

```python
# Configure inference endpoint (one-time setup)
PUT /_inference/completion/spec-generator
{
  "service": "openai",  # or "anthropic", "azure_openai", etc.
  "service_settings": {
    "api_key": "...",
    "model_id": "gpt-4o"  # or claude-sonnet, etc.
  }
}

# Generate a document
POST /_inference/completion/spec-generator
{
  "input": "Generate a PRD for: checkout form state loss\n\nBased on 45 feedback items...\n\n[full prompt here]"
}
```

This keeps everything inside the Elastic API surface.

---

## Phase 8 Changes

Minimal. The Slack integration, settings, responsive work, and polish are unchanged. The only difference:
- Settings > Connectors may show "Agent Builder" connection status instead of "Claude API" status
- No ANTHROPIC_API_KEY needed (but you need an LLM connector configured in Kibana)

---

## New Environment Variables

```env
# Replace these:
# ANTHROPIC_API_KEY=sk-ant-...      ← REMOVED
# AGENT_MODEL=claude-sonnet-4-20250514 ← REMOVED

# With these:
KIBANA_URL=https://your-deployment.kb.us-east-1.aws.elastic-cloud.com
KIBANA_API_KEY=your-kibana-api-key
AGENT_ID=context-engine-agent

# For spec generation (Phase 6) via ES Inference API:
SPEC_INFERENCE_ID=spec-generator
```

---

## New Dependencies

```
# Replace:
# anthropic>=0.39.0    ← REMOVED

# Add:
httpx>=0.27.0          # Async HTTP client for Kibana API calls
```

---

## Setup Script (run once per deployment)

Create `scripts/setup_agent.py`:

1. Configure LLM connector in Kibana (manual step — done in Kibana UI)
2. Register 7 ES|QL tools via Tools API
3. Register custom agent via Agents API
4. Configure ES Inference endpoint for spec generation
5. Test with a sample converse call

This script should be runnable: `python scripts/setup_agent.py`

---

## Summary for Cursor

When building Phase 5, tell Cursor:

> The agent uses Elastic Agent Builder, NOT Claude API. Read AGENT_ARCHITECTURE_UPDATE.md for the full architecture. The backend calls the Kibana Agent Builder converse API (`POST {KIBANA_URL}/api/agent_builder/converse`). Tools are ES|QL queries registered via the Agent Builder Tools API. Conversation history is managed by Agent Builder natively. The frontend is unchanged — it still calls our FastAPI backend, which proxies to Agent Builder.

When building Phase 6, tell Cursor:

> Spec generation uses the Elasticsearch Inference API (`POST /_inference/completion/{inference_id}`), NOT a direct Claude/OpenAI call. Read AGENT_ARCHITECTURE_UPDATE.md. The inference endpoint is configured in ES and called from Python via the ES client.
