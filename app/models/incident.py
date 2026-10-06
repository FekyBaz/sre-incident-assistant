from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high", "critical"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class IncidentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=10_000)
    severity: Severity = "medium"
    error_message: str | None = Field(default=None, max_length=5_000)
    github_repository: str | None = Field(default=None, max_length=200)


class Evidence(BaseModel):
    id: str
    source_type: Literal["log", "github_commit", "github_diff", "documentation", "other"]
    source_ref: str
    content: str
    relevance: float = Field(ge=0.0, le=1.0)


class Hypothesis(BaseModel):
    title: str
    explanation: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class Remediation(BaseModel):
    summary: str
    rationale: str
    human_review_required: bool = True


class InvestigationResult(BaseModel):
    incident: IncidentRequest
    summary: str
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    remediation: Remediation
    limitations: list[str] = Field(default_factory=list)
