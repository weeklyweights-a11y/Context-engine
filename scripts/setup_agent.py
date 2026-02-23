#!/usr/bin/env python3
"""
Setup Elastic Agent Builder tools and agent for an org.

Usage:
  cd Hackathon && python scripts/setup_agent.py <org_id>

Requires KIBANA_URL, KIBANA_API_KEY, AGENT_ID in Hackathon/.env
"""

import asyncio
import os
import sys

# Allow importing app from backend
_script_dir = os.path.dirname(os.path.abspath(__file__))
_hackathon_dir = os.path.dirname(_script_dir)
_backend_dir = os.path.join(_hackathon_dir, "backend")
sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from dotenv import load_dotenv

load_dotenv(os.path.join(_hackathon_dir, ".env"))


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python setup_agent.py <org_id>", file=sys.stderr)
        sys.exit(1)
    org_id = sys.argv[1].strip()
    if not org_id:
        print("org_id is required", file=sys.stderr)
        sys.exit(1)

    from app.services.agent_service import get_agent_service

    svc = get_agent_service()
    if not svc._enabled():
        print("Error: KIBANA_URL and KIBANA_API_KEY must be set in .env", file=sys.stderr)
        sys.exit(1)

    print(f"Registering tools for org {org_id}...")
    try:
        await svc.register_tools(org_id)
        print("Tools registered.")
    except Exception as e:
        print(f"Tool registration failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Registering agent for org {org_id}...")
    try:
        await svc.register_agent(org_id)
        print("Agent registered.")
    except Exception as e:
        print(f"Agent registration failed: {e}", file=sys.stderr)
        sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
