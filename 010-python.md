---
description: Python coding standards for all .py files
globs: "**/*.py"
alwaysApply: false
---

# Python Standards

## Style
- Python 3.11+ only
- Type hints on ALL function signatures. No exceptions.
- f-strings for formatting. Never .format() or %.
- pathlib for file paths. Never os.path.
- PEP 8 naming: snake_case for functions/variables, PascalCase for classes

## Structure
- Functions under 50 lines. Split if longer.
- Use dataclasses or Pydantic for data models
- One class per file unless tightly coupled
- Imports: stdlib first, third-party second, local third. Blank line between groups.

## Error Handling
- Use logging module, not print (except in scripts/)
- Always catch specific exceptions, never bare `except:`
- Elasticsearch calls MUST have try/except with meaningful error messages
- Connection failures should log the error AND suggest a fix

## Dependencies
- elasticsearch>=8.12.0 for ES client
- python-dotenv for env vars
- pyyaml for config
- NO unnecessary dependencies. Every pip install must be justified.

## Config
- Secrets in .env (never committed)
- Settings in config.yaml (committed with safe defaults)
- Always load with: `from dotenv import load_dotenv; load_dotenv()`
