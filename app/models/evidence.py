from pydantic import BaseModel, Field


class LogEntryEvidence(BaseModel):
    timestamp: str | None = None
    level: str | None = None
    message: str
    raw: str


class LogAnalysisResponse(BaseModel):
    format: str
    total_entries: int
    level_counts: dict[str, int] = Field(default_factory=dict)
    error_entries: list[LogEntryEvidence] = Field(default_factory=list)
    representative_entries: list[LogEntryEvidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
