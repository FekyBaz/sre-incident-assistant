from app.models.investigation import InvestigationRequest
from app.models.incident import Evidence, InvestigationResult, Remediation
from app.services.investigation import InvestigationService
from app.services.llm import LLMService


class FakeLLM(LLMService):
    def generate_structured(self, prompt: str, response_model):
        return InvestigationResult(
            incident=InvestigationRequest(
                incident={
                    "title": "API latency",
                    "description": "Requests became slow.",
                }
            ).incident,
            summary="Database latency is consistent with the supplied log evidence.",
            root_cause="Database timeout during request processing.",
            confidence=0.8,
            hypotheses=[],
            evidence=[],
            remediation=Remediation(
                summary="Investigate database timeout and connection health.",
                rationale="The supplied error evidence indicates a database timeout.",
            ),
        )


def test_investigation_rejects_missing_evidence():
    service = InvestigationService(
        llm_service=FakeLLM(),
    )
    request = InvestigationRequest(
        incident={
            "title": "Unknown failure",
            "description": "The service failed.",
        }
    )

    try:
        service.investigate(request)
    except Exception as exc:
        assert "No evidence" in str(exc)
    else:
        raise AssertionError("Expected investigation to fail without evidence")
