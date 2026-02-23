---
description: Project structure rules
globs:
alwaysApply: false
---

# Project Structure

```
context-engine-v2/
├── .cursor/rules/           # These rule files
├── .env                     # Secrets (NEVER commit)
├── .env.example             # Template for secrets
├── .gitignore
├── README.md                # For hackathon judges
├── PROJECT.md               # Full project context (AI reads this)
├── TASKS.md                 # Step-by-step implementation plan
├── LICENSE                  # MIT
├── requirements.txt
├── config.yaml              # Non-secret settings
├── scripts/
│   ├── generate_data.py     # Generate synthetic feedback
│   ├── ingest_data.py       # Bulk load into Elasticsearch
│   ├── create_index.py      # Set up ES indexes + mappings
│   ├── simulate_live.py     # Simulate real-time ingestion (bonus)
│   └── chat_with_agent.py   # Test agent via API (bonus)
├── src/
│   ├── __init__.py
│   ├── es_client.py         # ES connection singleton
│   ├── data_models.py       # Pydantic models for feedback, customer, product
│   └── utils.py             # Shared utilities
├── prompts/
│   ├── agent_system.md      # System prompt for the agent
│   └── spec_templates/      # Templates for 4-doc output
│       ├── prd.md
│       ├── architecture.md
│       ├── rules.md
│       └── plan.md
├── data/
│   ├── feedback.json        # Generated feedback data
│   ├── customers.json       # Generated customer profiles
│   └── product_context.json # Product info for Acme Analytics
└── docs/
    ├── architecture.md       # System architecture diagram
    └── demo_script.md        # Demo video script
```

## Rules
- New files go in the correct directory. Don't dump everything in root.
- Scripts that run once go in `scripts/`
- Reusable code goes in `src/`
- Data files go in `data/`
- Documentation goes in `docs/`
- Never create new top-level directories without a reason
