from app.models.incident import Evidence, IncidentRequest, InvestigationResult, Remediation
from app.services.report import render_incident_report


def test_report_contains_grounded_evidence():
    result = InvestigationResult(
        incident=IncidentRequest(title='API latency', description='Latency increased after deployment.'),
        summary='Database timeout evidence is present.',
        root_cause='Database timeout.',
        confidence=0.8,
        evidence=[Evidence(id='log-error-1', source_type='log', source_ref='app.log#error-1', content='ERROR database timeout', relevance=1.0)],
        remediation=Remediation(summary='Investigate database health.', rationale='The log contains a database timeout.'),
    )
    report = render_incident_report(result)
    assert '# SRE Incident Report' in report
    assert 'log-error-1' in report
    assert 'ERROR database timeout' in report


def test_report_renders_nonempty_hypotheses():
    from app.models.incident import Hypothesis

    result = InvestigationResult(
        incident=IncidentRequest(title="API latency", description="Slow requests."),
        summary="A database timeout occurred.",
        root_cause="Database pool pressure.",
        confidence=0.7,
        hypotheses=[Hypothesis(title="Pool exhaustion", explanation="Wait times rose.", confidence=0.8, supporting_evidence_ids=["log-error-1"], contradicting_evidence_ids=[])],
        evidence=[Evidence(id="log-error-1", source_type="log", source_ref="app.log", content="ERROR pool timeout", relevance=1.0)],
        remediation=Remediation(summary="Review pool configuration.", rationale="Pool waits observed."),
    )
    report = render_incident_report(result)
    assert "Supporting evidence: log-error-1" in report
    assert "Contradicting evidence: None" in report
