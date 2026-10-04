from __future__ import annotations

from app.models.incident import Evidence, InvestigationResult
from app.models.investigation import InvestigationRequest
from app.services.llm import LLMService, get_llm_service
from app.tools.github_client import GitHubClientError, get_github_client
from app.tools.log_analyzer import LogAnalyzer


class InvestigationError(RuntimeError):
    """Raised when an investigation cannot be completed safely."""


class InvestigationService:
    def __init__(
        self,
        llm_service: LLMService | None = None,
        log_analyzer: LogAnalyzer | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.log_analyzer = log_analyzer or LogAnalyzer()

    def build_evidence(self, request: InvestigationRequest) -> list[Evidence]:
        evidence: list[Evidence] = []

        if request.log_content.strip():
            analysis = self.log_analyzer.analyze(
                request.log_content,
                request.log_filename,
            )
            for index, entry in enumerate(analysis.error_entries, start=1):
                evidence.append(
                    Evidence(
                        id=f"log-error-{index}",
                        source_type="log",
                        source_ref=f"{request.log_filename}#error-{index}",
                        content=entry.raw,
                        relevance=1.0,
                    )
                )

            error_raw = {entry.raw for entry in analysis.error_entries}
            supplemental_entries = [
                entry
                for entry in analysis.representative_entries
                if entry.raw not in error_raw
            ][:10]
            for index, entry in enumerate(supplemental_entries, start=1):
                relevance = (
                    0.8
                    if entry.level and entry.level.upper() in {"WARN", "WARNING"}
                    else 0.6
                )
                evidence.append(
                    Evidence(
                        id=f"log-entry-{index}",
                        source_type="log",
                        source_ref=f"{request.log_filename}#entry-{index}",
                        content=entry.raw,
                        relevance=relevance,
                    )
                )

        if request.github_repository:
            client = get_github_client()
            try:
                commits = client.get_recent_commits(
                    request.github_repository,
                    limit=request.max_commits,
                )
            except GitHubClientError as exc:
                evidence.append(
                    Evidence(
                        id="github-error",
                        source_type="other",
                        source_ref=request.github_repository,
                        content=f"GitHub evidence collection failed: {exc}",
                        relevance=0.0,
                    )
                )
            else:
                for index, commit in enumerate(commits, start=1):
                    evidence.append(
                        Evidence(
                            id=f"github-commit-{index}",
                            source_type="github_commit",
                            source_ref=commit.url or commit.sha,
                            content=(
                                f"Commit {commit.sha}\n"
                                f"Message: {commit.message}\n"
                                f"Author: {commit.author or 'unknown'}\n"
                                f"Committed: {commit.committed_at or 'unknown'}\n"
                                f"Changed files: {', '.join(commit.files[:30]) or 'not available'}"
                            ),
                            relevance=max(0.4, 1.0 - (index - 1) * 0.07),
                        )
                    )

                for index, commit in enumerate(commits[:3], start=1):
                    try:
                        diff = client.get_commit_diff(request.github_repository, commit.sha)
                    except GitHubClientError as exc:
                        evidence.append(
                            Evidence(
                                id=f"github-diff-error-{index}",
                                source_type="other",
                                source_ref=commit.sha,
                                content=f"Commit diff collection failed: {exc}",
                                relevance=0.0,
                            )
                        )
                        continue

                    if diff.patch:
                        evidence.append(
                            Evidence(
                                id=f"github-diff-{index}",
                                source_type="github_diff",
                                source_ref=commit.sha,
                                content=(
                                    f"Commit: {diff.sha}\n"
                                    f"Message: {diff.message}\n"
                                    f"Files: {diff.files}\n"
                                    f"Patch:\n{diff.patch}"
                                )[:12_000],
                                relevance=max(0.7, 1.0 - (index - 1) * 0.1),
                            )
                        )

        return evidence

    def investigate(self, request: InvestigationRequest) -> InvestigationResult:
        evidence = self.build_evidence(request)
        if not evidence:
            raise InvestigationError(
                "No evidence was collected. Provide incident logs or a GitHub repository."
            )

        llm_service = self.llm_service or get_llm_service()
        evidence_text = "\n\n".join(
            f"[{item.id}] source={item.source_type} ref={item.source_ref}\n{item.content}"
            for item in evidence
        )

        prompt = f"""
You are an SRE incident investigation assistant.

Your job is to produce an evidence-grounded root cause analysis.
Do not invent facts, files, commits, metrics, or events.
Use ONLY the evidence supplied below.

Incident:
Title: {request.incident.title}
Description: {request.incident.description}
Severity: {request.incident.severity}
Error message: {request.incident.error_message or "not provided"}

Evidence:
{evidence_text}

Rules:
1. Generate plausible hypotheses, but distinguish hypotheses from established facts.
2. Every supporting or contradicting evidence ID must exactly match an ID in the supplied evidence.
3. The root_cause field must state the best-supported explanation and may say "undetermined" if evidence is insufficient.
4. Confidence must reflect evidence strength, not writing confidence.
5. Do not claim a code change caused the incident unless the evidence supports that connection.
6. Suggested remediation must be advisory and require human review.
7. List important limitations when evidence is missing, ambiguous, or contradictory.
8. Keep the result concise enough for an incident responder to review quickly.
"""

        try:
            result = self.llm_service.generate_structured(
                prompt,
                InvestigationResult,
            )
        except Exception as exc:
            raise InvestigationError("Investigation model failed.") from exc

        result.incident = request.incident
        result.evidence = evidence
        valid_ids = {item.id for item in evidence}
        for hypothesis in result.hypotheses:
            invalid = (
                set(hypothesis.supporting_evidence_ids)
                | set(hypothesis.contradicting_evidence_ids)
            ) - valid_ids
            if invalid:
                raise InvestigationError(
                    f"Model referenced evidence IDs that do not exist: {sorted(invalid)}"
                )

        return result
