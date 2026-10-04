from fastapi import APIRouter, Body, HTTPException

from app.models.evidence import LogAnalysisResponse
from app.models.incident import HealthResponse
from app.tools.github_client import GitHubClientError, get_github_client
from app.tools.log_analyzer import LogAnalyzer

router = APIRouter()
log_analyzer = LogAnalyzer()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="sre-incident-assistant")


@router.post("/api/v1/logs/analyze", response_model=LogAnalysisResponse, tags=["evidence"])
def analyze_logs(
    content: str = Body(..., media_type="text/plain"),
    filename: str = "incident.log",
) -> LogAnalysisResponse:
    analysis = log_analyzer.analyze(content, filename)
    return LogAnalysisResponse(
        format=analysis.format,
        total_entries=analysis.total_entries,
        level_counts=analysis.level_counts,
        error_entries=[
            {
                "timestamp": entry.timestamp,
                "level": entry.level,
                "message": entry.message,
                "raw": entry.raw,
            }
            for entry in analysis.error_entries
        ],
        representative_entries=[
            {
                "timestamp": entry.timestamp,
                "level": entry.level,
                "message": entry.message,
                "raw": entry.raw,
            }
            for entry in analysis.representative_entries
        ],
        warnings=analysis.warnings,
    )


@router.get("/api/v1/github/{owner}/{repo}/commits", tags=["evidence"])
def recent_commits(owner: str, repo: str, limit: int = 10):
    try:
        return {
            "repository": f"{owner}/{repo}",
            "commits": [
                commit.__dict__
                for commit in get_github_client().get_recent_commits(
                    f"{owner}/{repo}", limit=limit
                )
            ],
        }
    except GitHubClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/v1/github/{owner}/{repo}/commits/{commit_sha}", tags=["evidence"])
def commit_diff(owner: str, repo: str, commit_sha: str):
    try:
        diff = get_github_client().get_commit_diff(f"{owner}/{repo}", commit_sha)
        return diff.__dict__
    except GitHubClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
