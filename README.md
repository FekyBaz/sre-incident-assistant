# 🚀 SRE Incident Assistant

> 🏆 This repository is my official submission for the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

An AI-powered incident investigation assistant that combines LLM reasoning with structured evidence from application logs and Git repositories to accelerate Root Cause Analysis (RCA).

---

## 👤 Participant

| Field | Value |
| --- | --- |
| Full Name | Mohamed Elfeky |
| Project Name | SRE Incident Assistant |
| GitHub Username | [FekyBaz](https://github.com/FekyBaz) |
| Challenge Batch | June–July 2026 |
| Training Program | Large Language Models (LLMs) Program |
| Organization | [**Edrak for Ai**](https://edrak4ai.com/en) |

---

## 📖 Project Overview

When a production incident occurs, engineers often need to correlate information from application logs, recent deployments, Git commits, code changes, and technical documentation.

**SRE Incident Assistant** is designed to reduce this investigation effort by collecting relevant technical evidence and using an LLM to analyze it.

The system follows this workflow:

```text
Incident
   ↓
Evidence Collection
   ↓
Log Analysis + Git Analysis
   ↓
Hypothesis Generation
   ↓
Evidence Verification
   ↓
Root Cause Analysis
   ↓
Suggested Fix
   ↓
Incident Report
```

The assistant is designed as an investigation aid rather than an autonomous production operator. AI-generated conclusions should be verified by a human before changes are applied.

---

## ✨ Features

- 📝 Incident title, description, error message, and severity input
- 📄 Application log upload and analysis
- 🔎 Extraction of relevant errors, warnings, and timestamps
- 🐙 GitHub repository integration
- 📌 Recent commit retrieval
- 🔬 Commit and code-diff analysis
- 🧠 LLM-powered incident investigation
- 💡 Candidate hypothesis generation
- 🔗 Evidence-backed root cause analysis
- 📊 Confidence scoring
- 🛠️ Recommended remediation
- 📋 Structured incident report generation
- ⚠️ Explicit handling of insufficient evidence

---

## 🛠️ Technologies Used

### Core

- Python
- FastAPI
- Streamlit
- Pydantic

### AI

- Large Language Model API
- Structured LLM outputs
- Tool-based investigation workflow

### Integrations

- GitHub API

### Data Processing

- Python standard library
- Pandas where useful
- Log parsing and structured evidence extraction

The LLM provider is kept replaceable so the system can support different providers without changing the core investigation workflow.

---

## ⚙️ Installation

```bash
git clone https://github.com/FekyBaz/sre-incident-assistant.git
cd sre-incident-assistant

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -e ".[dev]"
```

Create a `.env` file based on `.env.example` and provide the required API credentials.

---

## 🚀 Usage

The intended MVP workflow is:

1. Enter an incident description.
2. Upload the relevant application logs.
3. Provide the GitHub repository URL.
4. Start the investigation.
5. Review extracted evidence.
6. Review candidate hypotheses.
7. Inspect the identified root cause and confidence.
8. Review the suggested remediation.
9. Generate the final incident report.

Detailed usage instructions and screenshots will be added with the completed MVP.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │        User         │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │      Streamlit      │
                    │         UI          │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Investigation Engine│
                    └──────────┬──────────┘
                               ↓
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
        ┌────────────┐   ┌────────────┐   ┌────────────┐
        │ Log Tools  │   │ Git Tools  │   │ Docs/RAG   │
        └────────────┘   └────────────┘   └────────────┘
                               ↓
                       ┌───────────────┐
                       │      LLM      │
                       └───────┬───────┘
                               ↓
                       ┌───────────────┐
                       │   Pydantic    │
                       │ Structured    │
                       │    Output     │
                       └───────┬───────┘
                               ↓
                       Incident Report
```

---

## 📸 Demo

The final demonstration will use a small repository containing a deliberately introduced software regression.

Example scenario:

> API latency increases after a deployment because a code change introduces an N+1 database query.

The assistant will analyze the incident, correlate the logs with recent Git changes, identify the likely regression, provide supporting evidence, and suggest a remediation.

Screenshots, GIFs, and the final demo video will be added after the MVP is completed.

---

## 📈 Results

The project will be evaluated using a small benchmark of known incidents.

Planned evaluation criteria include:

- Root cause accuracy
- Evidence relevance
- Hallucination rate
- Tool selection
- Structured output validity

Final quantitative results will be added after the evaluation phase.

---

## 🔮 Future Improvements

- Documentation RAG
- Metrics and observability integrations
- Multiple investigation agents
- Automatic patch generation
- Automated regression-test generation
- Slack and PagerDuty integrations
- Production observability integrations
- Post-mortem knowledge base
- Historical incident learning

These features are outside the initial MVP scope and will only be considered after the core workflow is stable.

---

## 📚 Project Documentation

The detailed project scope and implementation requirements are available in:

- [Project Specification](docs/PROJECT_SPECIFICATION.md)

---

## 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

## 📄 License

This project is shared for educational and portfolio purposes.


## Local Development

Install the project and development dependencies:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

Configure environment variables from `.env.example`, then run the API:

```bash
uvicorn app.main:app --reload
```

Open the interactive API docs at `/docs`.

Run the Streamlit demo:

```bash
streamlit run streamlit_app.py
```

The MVP accepts incident context, optional logs, and an optional GitHub repository. The investigation engine collects bounded evidence, asks the LLM for a structured RCA, validates evidence references, and renders a Markdown incident report.

## Evaluation

A five-scenario benchmark is available in `evaluation/benchmark.json`. The evaluation methodology is documented in `evaluation/README.md`.

## Demo Scenario

The repository includes an intentionally regressed N+1 query scenario under `demo/n_plus_one_regression/`.
It demonstrates the intended evidence chain: latency regression → elevated database query count → database timeout/pool wait → recent code change containing a database call inside a loop.

See `demo/n_plus_one_regression/README.md` for the walkthrough and `evaluation/n_plus_one_expected.json` for the expected RCA.

## Safety Boundary

The assistant is advisory. It does not modify production systems, deploy code, execute remediation, or treat an LLM conclusion as established fact without evidence.