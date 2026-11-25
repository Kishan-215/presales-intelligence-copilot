"""Dashboard: headline numbers and pipeline status."""
import pandas as pd
import streamlit as st

from modules.pipeline import FULL_KEYS
from ui_common import show_mode_banner


def render() -> None:
    st.title("Dashboard")
    extraction = st.session_state.get("extraction")
    clarification = st.session_state.get("clarification")
    risks = st.session_state.get("risks")
    estimate = st.session_state.get("estimate")

    if extraction is None:
        st.info("Load a document on **Upload Requirements** and run the analysis to populate the dashboard.")
        project_name, n_req, n_high, n_q = "No project loaded", "-", "-", "-"
    else:
        show_mode_banner()
        reqs = extraction.data.requirements
        project_name = extraction.data.overview.project_name
        n_req = len(reqs)
        n_high = sum(1 for r in reqs if r.priority == "High")
        n_q = len(clarification.data.questions) if clarification else "-"

    st.subheader(project_name)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Requirements", n_req)
    c2.metric("High priority", n_high)
    c3.metric("Clarification questions", n_q)
    c4.metric("Identified risks", len(risks.data.risks) if risks else "-")
    c5.metric("Estimated person-days", f"{estimate.overall_min}-{estimate.overall_max}" if estimate else "-")

    st.markdown("#### Pipeline status")
    rows = []
    for label, key in [
        ("Requirement extraction", "extraction"),
        ("Clarification questions", "clarification"),
        ("Project classification", "classification"),
        ("Risk analysis", "risks"),
        ("Effort estimation", "effort_inputs"),
        ("Architecture recommendation", "architecture"),
        ("Technical roadmap", "roadmap"),
    ]:
        stage = st.session_state.get(key)
        rows.append({"Stage": label, "Status": "Done" if stage else "Not run", "Mode": stage.mode if stage else "-"})
    ready = all(st.session_state.get(k) is not None for k in FULL_KEYS)
    rows.append({"Stage": "Proposal report", "Status": "Ready to generate" if ready else "Waiting for analysis", "Mode": "-"})
    st.dataframe(pd.DataFrame(rows).set_index("Stage"))