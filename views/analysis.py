"""Requirement Analysis page: overview, requirements table, clarification questions, classification."""
import pandas as pd
import streamlit as st

from modules.clarification_generator import detect_gaps
from ui_common import show_mode_banner


def _bullets(title: str, items) -> None:
    st.markdown(f"**{title}**")
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption("Not specified")


def _overview_tab(ov) -> None:
    c1, c2 = st.columns(2)
    c1.metric("Client industry", ov.client_industry)
    c2.metric("Cloud preference", ov.cloud_preferences)
    st.markdown("**Business problem**")
    st.write(ov.business_problem)
    left, right = st.columns(2)
    with left:
        _bullets("Business objectives", ov.business_objectives)
        _bullets("Target users", ov.target_users)
        _bullets("Required integrations", ov.required_integrations)
        _bullets("Data sources", ov.data_sources)
        _bullets("Constraints", ov.constraints)
        _bullets("Dependencies", ov.dependencies)
    with right:
        _bullets("Security requirements", ov.security_requirements)
        _bullets("Compliance requirements", ov.compliance_requirements)
        _bullets("Performance requirements", ov.performance_requirements)
        _bullets("Scalability requirements", ov.scalability_requirements)
        st.markdown("**Budget**")
        st.write(ov.budget_information)
        st.markdown("**Timeline**")
        st.write(ov.timeline_information)


def _requirements_tab(extraction) -> None:
    reqs = extraction.data.requirements
    if not reqs:
        st.info("No requirements were extracted.")
        return
    df = pd.DataFrame(
        [
            {
                "ID": r.requirement_id,
                "Requirement": r.description,
                "Category": r.category,
                "Priority": r.priority,
                "Confidence": r.confidence,
                "Missing information": r.missing_information,
            }
            for r in reqs
        ]
    )
    f1, f2 = st.columns(2)
    categories = f1.multiselect("Filter by category", sorted(df["Category"].unique()))
    priorities = f2.multiselect("Filter by priority", ["High", "Medium", "Low"])
    if categories:
        df = df[df["Category"].isin(categories)]
    if priorities:
        df = df[df["Priority"].isin(priorities)]
    st.dataframe(df, hide_index=True)
    st.caption("Confidence is reported by the model itself and is not a calibrated probability.")

    st.markdown("#### Inspect a requirement")
    chosen = st.selectbox("Requirement", [r.requirement_id for r in reqs])
    req = next(r for r in reqs if r.requirement_id == chosen)
    st.write(req.description)
    st.markdown("**Source excerpt from the document**")
    st.markdown(f"> {req.source_excerpt}")
    st.markdown(f"**Missing information:** {req.missing_information}")
    if req.notes:
        if "verify manually" in req.notes:
            st.warning(req.notes)
        else:
            st.markdown(f"**Notes:** {req.notes}")

    st.download_button(
        "Download requirements (JSON)",
        data=extraction.data.model_dump_json(indent=2),
        file_name="requirements.json",
        mime="application/json",
    )


def _questions_tab(clarification, extraction) -> None:
    questions = clarification.data.questions
    if not questions:
        st.info("No clarification questions were generated.")
    for i, q in enumerate(questions, start=1):
        st.markdown(f"**{i}. [{q.priority}] {q.question}**")
        related = ", ".join(q.related_requirement_ids) if q.related_requirement_ids else "whole project"
        st.caption(f"Why it matters: {q.reason}  |  Related: {related}")
    doc = st.session_state.get("document")
    if doc is not None:
        with st.expander("Rule-based gap check (information the document does not mention)"):
            gaps = detect_gaps(doc.text, extraction.data.overview)
            if gaps:
                for _, label in gaps:
                    st.markdown(f"- {label}")
            else:
                st.write("No standard gaps detected.")


def _classification_tab(classification) -> None:
    items = classification.data.classifications
    if not items:
        st.info("No classification was produced.")
    for item in items:
        with st.container(border=True):
            st.markdown(f"**{item.category}**")
            st.write(item.reasoning)

def _risks_tab(stage) -> None:
    if stage is None:
        st.info("Risk analysis has not been run yet.")
        return
    data = stage.data
    if data.risks:
        df = pd.DataFrame(
            [
                {"ID": r.risk_id, "Severity": r.severity, "Risk": r.description, "Related requirement": r.related_requirement}
                for r in data.risks
            ]
        ).set_index("ID")
        st.dataframe(df)
        for r in data.risks:
            with st.expander(f"{r.risk_id} [{r.severity}] {r.description[:90]}"):
                st.markdown(f"**Potential impact:** {r.potential_impact}")
                st.markdown(f"**Suggested mitigation:** {r.suggested_mitigation}")
                st.markdown(f"**Related requirement:** {r.related_requirement}")
    c1, c2, c3 = st.columns(3)
    with c1:
        _bullets("Confirmed facts (stated in the document)", data.confirmed_facts)
    with c2:
        _bullets("Assumptions (made by this draft)", data.assumptions)
    with c3:
        _bullets("Unknowns (information still missing)", data.unknowns)

def render() -> None:
    st.title("Requirement Analysis")
    extraction = st.session_state.get("extraction")
    if extraction is None:
        st.info("No analysis yet. Open **Upload Requirements**, load a document and run the analysis.")
        return
    show_mode_banner()
    st.subheader(extraction.data.overview.project_name)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Requirements", "Clarification questions", "Project classification", "Risks and assumptions"]
    )
    with tab1:
        _overview_tab(extraction.data.overview)
    with tab2:
        _requirements_tab(extraction)
    with tab3:
        _questions_tab(st.session_state["clarification"], extraction)
    with tab4:
        _classification_tab(st.session_state["classification"])
    with tab5:
        _risks_tab(st.session_state.get("risks"))   
