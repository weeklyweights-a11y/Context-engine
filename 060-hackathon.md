---
description: Hackathon competition rules — the judge perspective
globs:
alwaysApply: true
---

# Hackathon Rules — We're Here to WIN

## Deadline: Feb 27, 2026. No extensions.

## What Judges Care About
1. **Does it work?** A working demo beats a broken masterpiece.
2. **Does it use Elasticsearch deeply?** Vector search, ES|QL, Agent Builder, Kibana dashboards, hybrid search — show them ALL.
3. **Is it impressive?** The 4-doc spec output (PRD + Architecture + Rules + Plan) from customer feedback is our wow moment.
4. **Is the video good?** 3 minutes, clear story, visible results.
5. **Is the repo clean?** README with screenshots, clear setup instructions, MIT license.

## Decision Framework
Before ANY task, ask: "Does this help us win the hackathon?"
- YES → Do it
- MAYBE → Do it only if core features are done
- NO → Skip it

## Priority Stack (in order)
1. Data in Elasticsearch with working search (Days 1-2)
2. Agent with tools that answer questions (Days 3-4)
3. Kibana dashboards showing monitoring (Day 5)
4. 4-doc spec generation working (Day 5-6)
5. README + screenshots (Day 7)
6. Demo video (Day 8-9)
7. MCP/Slack/extras (ONLY if 1-6 are solid)

## Anti-Patterns to Avoid
- Building a custom frontend when Kibana exists
- Spending 2 days on perfect data when good-enough data works
- Adding features nobody asked for
- Optimizing code that runs once
- Writing tests for hackathon code (controversial but real — ship first)
- Over-documenting internal code (document the README instead)

## The Demo Story
"PM opens Kibana → sees feedback dashboard → spots checkout spike → asks agent what's happening → agent explains with data → PM says 'generate specs' → agent produces 4 documents backed by real customer data → from spike to engineering-ready spec in 2 minutes."

That story must work flawlessly on demo day.
