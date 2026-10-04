from pydantic import BaseModel, Field

from app.models.incident import IncidentRequest, InvestigationResult


class InvestigationRequest(BaseModel):
    incident: IncidentRequest
    log_content: str = Field(default="", max_length=200_000)
    log_filename: str = Field(default="incident.log", max_length=200)
    github_repository: str | None = Field(default=None, max_length=300)
    max_commits: int = Field(default=8, ge=1, le=20)


class InvestigationResponse(BaseModel):
    result: InvestigationResult
    evidence_count: int
    evidence_sources: list[str]
