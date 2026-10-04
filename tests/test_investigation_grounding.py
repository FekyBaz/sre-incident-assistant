from app.models.investigation import InvestigationRequest
from app.models.incident import Hypothesis, InvestigationResult, Remediation
from app.services.investigation import InvestigationError, InvestigationService
from app.services.llm import LLMService


class UngroundedLLM(LLMService):
    def generate_structured(self, prompt: str, response_model):
        return InvestigationResult(
            incident=InvestigationRequest(
                incident={"title": "Failure", "description": "Service failed."}
            ).incident,
            summary="Unsupported result.",
            root_cause="Unknown",
            confidence=0.2,
            hypotheses=[
                Hypothesis(
                    title="Unsupported hypothesis",
                    explanation="This cites evidence that was never collected.",
                    supporting_evidence_ids=["does-not-exist"],
                    confidence=0.2,
                )
            ],
            evidence=[],
            remediation=Remediation(
                summary="Investigate manually.",
                rationale="Evidence is insufficient.",
            ),
        )


def test_invalid_evidence_references_are_rejected():
    service = InvestigationService(llm_service=UngroundedLLM())
    request = InvestigationRequest(
        incident={"title": "Failure", "description": "Service failed."},
        log_content="2026-10-04T10:00:00Z ERROR database timeout",
    )

    try:
        service.investigate(request)
    except InvestigationError as exc:
        assert "evidence IDs" in str(exc)
    else:
        raise AssertionError("Expected ungrounded evidence to be rejected")
