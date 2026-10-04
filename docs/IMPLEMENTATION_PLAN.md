# Implementation Plan

## Goal
Deliver a focused MVP of SRE Incident Assistant for the Tips Hindawi LLMs Internship: an evidence-backed incident investigation assistant that correlates incident logs with recent GitHub changes and produces a structured RCA.

## Execution principles
- Build the smallest credible end-to-end slice first.
- Evidence before conclusions: every RCA claim should point to observed evidence.
- Human-in-the-loop: recommendations are advisory; no production changes.
- Keep the architecture provider-agnostic and avoid unnecessary infrastructure.

## Milestones

### M1 — Foundation
- Python project structure
- Configuration and environment handling
- FastAPI application
- Pydantic domain/request/response models
- LLM provider abstraction
- Health check and basic incident endpoint

### M2 — Evidence Collection
- Log upload and parsing for TXT/LOG/JSON
- Log normalization and useful summaries
- GitHub repository validation
- Recent commit retrieval
- Commit diff retrieval
- Evidence model with source/type/content/reference

### M3 — Investigation Engine
- Incident context assembly
- Hypothesis generation
- Evidence matching/correlation
- Root-cause ranking
- Confidence scoring
- Suggested remediation
- Strict structured output validation

### M4 — User Experience
- Streamlit incident form
- Log upload
- GitHub repo input
- Investigation progress/state
- Evidence + hypotheses + RCA display
- Incident report export/display

### M5 — Evaluation & Submission Polish

Current status: engineering MVP implemented; remaining work is benchmark execution, final documentation, and submission packaging.
- Five known incident scenarios
- RCA accuracy/evidence relevance checks
- Hallucination guard checks
- Demo scenario
- README completion
- Architecture diagram and final documentation

## Dependency order
M1 → M2 → M3 → M4 → M5

The first vertical slice should be usable as soon as M1 + a minimal M2 are complete.