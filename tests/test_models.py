import pytest
from pydantic import ValidationError

from app.models.incident import IncidentRequest, InvestigationResult


def test_incident_request_defaults():
    incident = IncidentRequest(
        title="API latency regression",
        description="Latency increased after deployment.",
    )

    assert incident.severity == "medium"
    assert incident.error_message is None


def test_incident_request_rejects_empty_title():
    with pytest.raises(ValidationError):
        IncidentRequest(title="", description="Something failed.")


def test_investigation_result_validates_confidence_range():
    with pytest.raises(ValidationError):
        InvestigationResult(
            incident=IncidentRequest(
                title="Failure",
                description="Service failed.",
            ),
            summary="summary",
            root_cause="unknown",
            confidence=1.5,
            remediation={
                "summary": "Investigate",
                "rationale": "Evidence is incomplete.",
            },
        )
