# SRE Incident Assistant — Project Specification

## AI-Powered Incident Investigation & Root Cause Analysis

### 1. Project Overview

**SRE Incident Assistant** is an AI-assisted system for investigating software incidents and identifying likely root causes.

Instead of manually inspecting thousands of log lines, recent Git commits, code changes, and technical documentation, the system collects relevant evidence and uses an LLM to analyze it and produce:

- Incident summary
- Relevant evidence
- Candidate hypotheses
- Most likely root cause
- Confidence score
- Recommended fix
- Shareable incident report

> The system assists SREs and software engineers; it does not replace human review.

### 2. Problem Statement

During a production incident, engineers often need to correlate information across application logs, deployments, Git history, code changes, configuration, and documentation. This investigation can be slow and fragmented.

The system aims to accelerate this process by combining LLM reasoning with explicit tools that retrieve and analyze technical evidence.

### 3. Project Goal

Build a workflow:

Incident → Evidence Collection → Evidence Analysis → Hypotheses → Verification → Root Cause → Suggested Fix → Incident Report

The system should ground important conclusions in available evidence rather than producing unsupported guesses.

### 4. Target User

Software engineers, SREs, and DevOps engineers investigating application incidents.

### 5. MVP Scope

The MVP includes:

- Incident title and description
- Error message and optional severity
- Upload of .log, .txt, and .json logs
- Log parsing and relevant-event extraction
- GitHub repository input
- Recent commit retrieval
- Commit diff inspection
- LLM-based investigation
- Hypothesis generation and evidence matching
- Root Cause Analysis
- Confidence score
- Suggested fix
- Incident report
- Simple Streamlit UI

### 6. Log Analysis

The system should parse uploaded logs, identify errors and warnings, extract timestamps, and surface entries relevant to the incident.

Large logs should be processed rather than blindly sending the entire file to the LLM.

### 7. GitHub Integration

For a supplied repository, the system should retrieve recent commits and relevant diffs to identify code changes that may correlate with the incident.

### 8. AI Investigation Engine

The investigation engine combines:

Incident + Logs + Git changes (+ optional documentation)

It should generate candidate hypotheses and evaluate them against available evidence.

### 9. Evidence-Based Reasoning

Major conclusions should include supporting evidence, such as commit identifiers, log references, and relevant observations.

When evidence is insufficient, the system should explicitly report that the root cause cannot be determined reliably and recommend additional investigation.

### 10. Structured Output

LLM responses should be represented as validated structured data using Pydantic models.

A representative analysis object includes:

- incident_summary
- severity
- hypotheses
- confidence
- evidence references
- root_cause
- recommended_fix
- additional_investigation

### 11. Suggested Fix

The MVP produces recommendations for human review. It does not automatically modify production code or deploy changes.

### 12. Incident Report

The system should generate a concise report containing incident summary, impact, timeline, root cause, confidence, evidence, recommended fix, and follow-up actions.

### 13. Architecture

```
User
  ↓
Streamlit UI
  ↓
FastAPI Backend
  ↓
Investigation Engine
  ├── Log Tools
  ├── GitHub Tools
  └── Optional Documentation Search
  ↓
LLM
  ↓
Pydantic Structured Output
  ↓
Evidence-backed Incident Report
```

### 14. Technology Stack

- Python
- FastAPI
- Streamlit
- Gemini API or OpenAI API
- GitHub API
- Pydantic
- Pandas / Python standard library for log processing
- SQLite only if persistence is needed for the MVP

The LLM provider should remain replaceable.

### 15. Core Tools

- `analyze_logs()`
- `get_recent_commits()`
- `get_commit_diff(commit_sha)`
- Optional: `search_documentation(query)`

### 16. Investigation Workflow

1. Receive incident
2. Parse incident description
3. Analyze logs
4. Retrieve recent commits
5. Identify potentially relevant changes
6. Generate hypotheses
7. Compare hypotheses against evidence
8. Select the most likely root cause
9. Generate recommended fix
10. Generate final incident report

### 17. Human-in-the-Loop

The UI should clearly state:

> AI-generated analysis — verify before applying changes.

The system must not imply certainty when evidence is weak.

### 18. Evaluation

Create a small benchmark of known incidents with known causes.

Measure:

- Root cause accuracy
- Evidence relevance
- Hallucination rate
- Tool selection
- Structured output validity

### 19. Demo Scenario

Use a small repository with a deliberately introduced regression, for example an N+1 database query.

A typical demo flow:

1. Healthy API latency
2. Deploy a commit introducing a regression
3. Logs show increased database activity and latency
4. Submit the incident
5. Assistant retrieves logs and recent Git changes
6. Assistant identifies the regression and cites supporting evidence
7. Assistant proposes a remediation

### 20. MVP vs Future Features

MVP:

- Incident input
- Log upload
- Log analysis
- GitHub integration
- Commit and diff analysis
- Root Cause Analysis
- Evidence
- Confidence
- Suggested fix
- Incident report
- Simple UI

Future possibilities:

- Documentation RAG
- Metrics integrations
- Multi-agent orchestration
- Automatic patch generation
- Automated test generation
- Slack / PagerDuty integrations
- Production observability integrations
- Post-mortem knowledge base

### 21. Repository Structure

```
sre-incident-assistant/
├── app/
│   ├── main.py
│   ├── api/
│   ├── agents/
│   ├── tools/
│   ├── models/
│   ├── services/
│   └── utils/
├── ui/
├── tests/
├── evaluation/
├── sample_data/
├── .env.example
├── requirements.txt
├── README.md
└── LICENSE
```

### 22. Implementation Plan

**Phase 1 — Foundation**

- Repository setup
- FastAPI
- Streamlit
- Pydantic models
- LLM integration
- Basic incident endpoint

**Phase 2 — Evidence**

- Log parser
- Log analysis
- GitHub API
- Commit retrieval
- Diff retrieval

**Phase 3 — Investigation**

- Investigation workflow
- Hypothesis generation
- Evidence matching
- Root Cause Analysis
- Structured outputs

**Phase 4 — Presentation**

- Streamlit UI
- Evidence display
- Suggested fix
- Final report

**Phase 5 — Polish (optional)**

- Evaluation benchmark
- Error handling
- README
- Architecture diagram
- Demo scenario
- Demo video

### 23. Success Criteria

The MVP is complete when a user can:

1. Enter an incident
2. Upload logs
3. Provide a GitHub repository
4. Start an investigation
5. See relevant evidence
6. See candidate hypotheses
7. Receive a root cause analysis
8. See confidence and supporting evidence
9. Receive a suggested fix
10. Generate an incident report

### 24. Project Positioning

The project should be presented as:

> **An AI-powered incident investigation system that combines LLM reasoning with structured evidence retrieval from application logs and Git repositories to accelerate root cause analysis.**

The central concept is:

**LLM + Tools + Evidence + Reasoning**

### 25. Final Scope Decision

The project prioritizes:

**Speed → Reliability → Demonstrable AI capability → Engineering quality**

The initial implementation intentionally avoids unnecessary complexity. Multi-agent architecture, vector databases, production infrastructure, autonomous code modification, and other advanced features are optional extensions rather than MVP requirements.
