import streamlit as st

from app.models.investigation import InvestigationRequest
from app.services.investigation import InvestigationError, InvestigationService
from app.services.report import render_incident_report

st.set_page_config(
    page_title="SRE Incident Assistant",
    page_icon="🚨",
    layout="wide",
)

st.title("🚨 SRE Incident Assistant")
st.caption("Evidence-backed incident investigation and root cause analysis.")

with st.form("incident_form"):
    title = st.text_input("Incident title", placeholder="API latency regression")
    description = st.text_area(
        "Incident description",
        placeholder="Latency increased after the latest deployment.",
    )
    severity = st.selectbox("Severity", ["low", "medium", "high", "critical"], index=1)
    error_message = st.text_input("Error message (optional)")
    repository = st.text_input(
        "GitHub repository",
        placeholder="owner/repository or https://github.com/owner/repository",
    )
    uploaded = st.file_uploader(
        "Incident log (.log, .txt, .json)",
        type=["log", "txt", "json"],
    )
    submitted = st.form_submit_button("Investigate", type="primary")

if submitted:
    if not title or not description:
        st.error("Incident title and description are required.")
        st.stop()

    log_content = ""
    log_filename = "incident.log"
    if uploaded is not None:
        log_content = uploaded.getvalue().decode("utf-8", errors="replace")
        log_filename = uploaded.name

    request = InvestigationRequest(
        incident={
            "title": title,
            "description": description,
            "severity": severity,
            "error_message": error_message or None,
            "github_repository": repository or None,
        },
        log_content=log_content,
        log_filename=log_filename,
        github_repository=repository or None,
    )

    with st.spinner("Collecting evidence and investigating..."):
        try:
            result = InvestigationService().investigate(request)
        except InvestigationError as exc:
            st.error(str(exc))
            st.stop()

    st.success("Investigation completed.")

    summary_col, confidence_col = st.columns(2)
    with summary_col:
        st.subheader("Root Cause")
        st.write(result.root_cause)
    with confidence_col:
        st.subheader("Confidence")
        st.metric("Confidence", f"{result.confidence:.0%}")

    st.subheader("Evidence")
    for item in result.evidence:
        with st.expander(f"{item.id} · {item.source_type} · relevance {item.relevance:.0%}"):
            st.caption(item.source_ref)
            st.code(item.content[:8000])

    st.subheader("Hypotheses")
    for hypothesis in result.hypotheses:
        st.markdown(f"**{hypothesis.title}** — {hypothesis.confidence:.0%}")
        st.write(hypothesis.explanation)
        st.caption(
            "Supporting: "
            + (", ".join(hypothesis.supporting_evidence_ids) or "None")
        )

    st.subheader("Recommended Remediation")
    st.write(result.remediation.summary)
    st.write(result.remediation.rationale)
    st.warning("Human review is required before any production change.")

    st.subheader("Incident Report")
    report = render_incident_report(result)
    st.download_button(
        "Download Markdown report",
        data=report,
        file_name="incident-report.md",
        mime="text/markdown",
    )
    st.code(report, language="markdown")
