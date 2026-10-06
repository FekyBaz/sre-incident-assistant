from app.models.investigation import InvestigationRequest
from app.services.investigation import InvestigationService


def test_warn_evidence_is_preserved_in_build_evidence():
    with open("demo/n_plus_one_regression/incident.log") as f:
        log_content = f.read()
    request = InvestigationRequest(
        incident={"title": "API latency", "description": "Latency up."},
        log_content=log_content,
    )
    evidence = InvestigationService().build_evidence(request)
    contents = "\n".join(item.content for item in evidence)
    assert "queries=51" in contents
    assert "pool_wait_ms=3100" in contents
    assert any(item.id.startswith("log-entry-") for item in evidence)
