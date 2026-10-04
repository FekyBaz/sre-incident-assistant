from app.models.incident import InvestigationResult


def render_incident_report(result: InvestigationResult) -> str:
    lines = [
        '# SRE Incident Report',
        '',
        '## Incident',
        f'- **Title:** {result.incident.title}',
        f'- **Severity:** {result.incident.severity}',
        f'- **Description:** {result.incident.description}',
        '',
        '## Root Cause',
        result.root_cause,
        '',
        f'**Confidence:** {result.confidence:.0%}',
        '',
        '## Summary',
        result.summary,
        '',
        '## Hypotheses',
    ]

    if result.hypotheses:
        for index, hypothesis in enumerate(result.hypotheses, start=1):
            lines.extend([
                f'### {index}. {hypothesis.title}',
                hypothesis.explanation,
                f'- Confidence: {hypothesis.confidence:.0%}',
                f'- Supporting evidence: {supporting}',
                f'- Contradicting evidence: {contradicting}',
                '',
            ])
    else:
        lines.extend(['No additional hypotheses were generated.', ''])

    lines.extend(['## Evidence', ''])
    for item in result.evidence:
        lines.extend([
            f'### {item.id}',
            f'- Source: {item.source_type}',
            f'- Reference: {item.source_ref}',
            f'- Relevance: {item.relevance:.0%}',
            '',
            '```text',
            item.content[:4000],
            '```',
            '',
        ])

    lines.extend([
        '## Recommended Remediation',
        result.remediation.summary,
        '',
        result.remediation.rationale,
        '',
        f'**Human review required:** {result.remediation.human_review_required}',
        '',
        '## Limitations',
    ])
    if result.limitations:
        lines.extend(f'- {item}' for item in result.limitations)
    else:
        lines.append('- No additional limitations reported by the investigation model.')
    return '\n'.join(lines)