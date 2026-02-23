---
description: Elasticsearch rules for any file touching ES
globs: "src/**/*.py,scripts/**/*.py"
alwaysApply: false
---

# Elasticsearch Rules

## Client
- Single client instance via `src/es_client.py`. Never create new clients elsewhere.
- Always use API key auth, never username/password for cloud
- Connection pattern:
```python
from elasticsearch import Elasticsearch
es = Elasticsearch(
    cloud_id=os.getenv("ELASTICSEARCH_CLOUD_ID"),
    api_key=os.getenv("ELASTICSEARCH_API_KEY"),
)
```

## Indexing
- Bulk API for 10+ documents. Never loop individual index calls.
- Always check bulk response for errors:
```python
success, errors = helpers.bulk(es, actions, raise_on_error=False)
if errors:
    logging.error(f"Bulk indexing had {len(errors)} errors")
```
- Index names: `feedback` for main data, `customers` for customer profiles, `product-context` for product info

## Querying
- Use ES|QL for aggregations and analytics
- Use standard query DSL for search (semantic, keyword, hybrid)
- Always include `size` parameter — never rely on defaults
- Always handle empty results gracefully

## ES|QL Syntax
- Pipe-based: `FROM index | WHERE condition | STATS agg BY field | SORT field`
- String comparison uses `==` not `=`
- Date filtering: `WHERE created_at >= "2026-01-01"`
- Always test queries in Kibana Dev Tools first

## Semantic Search
- Use ELSER if available on deployment
- Fall back to dense_vector with sentence-transformers if ELSER unavailable
- Hybrid search combines keyword + semantic — use for all user-facing searches

## DO NOT
- Never use `match_all` in production queries
- Never ignore bulk errors
- Never hardcode index names — use config
- Never assume a field exists — check mapping first
