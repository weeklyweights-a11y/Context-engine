---
description: Rules for generating synthetic feedback and customer data
globs: "scripts/generate_data.py,data/**"
alwaysApply: false
---

# Data Generation Rules

## Feedback Data (800 items)
- Must sound like REAL humans. Not "This is bad" but "I've been trying to complete a purchase for 20 minutes and the payment form keeps resetting. This is incredibly frustrating."
- Vary length: some are one line, some are a paragraph
- Vary tone: angry, disappointed, confused, grateful, excited
- Include typos occasionally for realism
- Mix styles: mostly formal, some casual/Slack-style

## Required Clusters (these MUST be visible in the data)
- ~100 checkout complaints (form reset, too many steps, bad errors, no progress bar)
- ~80 pricing concerns (too expensive, competitor comparison, value unclear)
- ~60 dashboard performance (slow loading, timeout, lag)
- ~50 onboarding confusion (unclear steps, no guidance, lost)
- ~510 distributed across remaining areas with mixed sentiment

## Temporal Patterns (these make dashboards interesting)
- Checkout: steady increase over 8 weeks (gets worse each week)
- Pricing: spike in last 2 weeks (sudden new problem)
- Dashboard: stable/flat over time
- Onboarding: slight decrease (improving)
- More data in recent weeks than early weeks

## Customer Data (50-100 profiles)
- Realistic company names (not "Company A")
- Segments: enterprise (20%), SMB (40%), consumer (25%), trial (15%)
- Enterprise: $500-5000/month MRR, named account managers
- Include 3 enterprise accounts with renewals in next 60 days
- Include health scores (0-100)
- Include industry tags

## Product Context
- Product: Acme Analytics (B2B SaaS data analytics platform)
- 8 product areas with team ownership
- Q1 2026 priorities defined
- Customer segment revenue breakdown

## Format
- All data as JSON arrays
- Dates in ISO 8601: "2026-02-10T14:30:00Z"
- IDs prefixed: fb_001, cust_001
- Every feedback item MUST have a customer_id linking to customers index
