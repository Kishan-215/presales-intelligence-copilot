"""Effort Estimation page: AI suggests complexity labels, Python calculates the person-days."""
import pandas as pd
import streamlit as st

import llm_client
from modules.common import DemoUnavailableError
from modules.effort_estimator import calculate_estimate, suggest_effort_inputs
from schemas import EffortInputs
from ui_common import show_mode_banner

SIZES = ["Small", "Medium", "Large"]
SECURITY = ["Standard", "High"]
CLARITY = ["Clear", "Partial", "Unclear"]
AI_LEVELS = ["None", "Low", "Medium", "High"]


def _load_widgets(inputs: EffortInputs) -> None:
    st.session_state["ei_size"] = inputs.size
    st.session_state["ei_integrations"] = inputs.integration_count
    st.session_state["ei_security"] = inputs.security_level
    st.session_state["ei_clarity"] = inputs.requirement_clarity
    st.session_state["ei_ai"] = inputs.ai_complexity
    st.session_state["ei_mobile"] = inputs.has_mobile_app


def _current_inputs(suggested: EffortInputs) -> EffortInputs:
    return EffortInputs(
        size=st.session_state["ei_size"],
        integration_count=st.session_state["ei_integrations"],
        security_level=st.session_state["ei_security"],
        requirement_clarity=st.session_state["ei_clarity"],
        ai_complexity=st.session_state["ei_ai"],
        has_mobile_app=st.session_state["ei_mobile"],
        rationale=suggested.rationale,
    )


def _same(a: EffortInputs, b: EffortInputs) -> bool:
    return a.model_dump(exclude={"rationale"}) == b.model_dump(exclude={"rationale"})


def _suggest(doc_text, extraction, classification) -> None:
    try:
        with st.spinner("Choosing complexity inputs..."):
            stage = suggest_effort_inputs(
                doc_text, extraction.data, classification.data, use_demo=st.session_state.get("use_demo", False)
            )
    except DemoUnavailableError as e:
        st.error(str(e))
        return
    except llm_client.LLMError as e:
        st.error(f"The AI service could not suggest estimate inputs: {e}")
        return
    except Exception as e:
        st.error(f"Unexpected error: {type(e).__name__}: {e}")
        return
    st.session_state["effort_inputs"] = stage
    _load_widgets(stage.data)


def render() -> None:
    st.title("Effort Estimation")
    st.caption("The AI suggests complexity labels. All person-day totals and contingency are calculated by fixed Python rules.")

    extraction = st.session_state.get("extraction")
    classification = st.session_state.get("classification")
    document = st.session_state.get("document")
    if extraction is None or classification is None or document is None:
        st.info("Run the analysis on **Upload Requirements** first.")
        return

    if st.button("Suggest inputs and calculate estimate", type="primary"):
        _suggest(document.text, extraction, classification)

    stage = st.session_state.get("effort_inputs")
    if stage is None:
        st.info("Click the button above to generate the estimate.")
        return

    show_mode_banner()
    if "ei_size" not in st.session_state:
        _load_widgets(stage.data)

    with st.expander("Adjust complexity inputs (what-if)"):
        c1, c2, c3 = st.columns(3)
        c1.selectbox("Project size", SIZES, key="ei_size")
        c2.number_input("External integrations", min_value=0, max_value=15, step=1, key="ei_integrations")
        c3.selectbox("Security level", SECURITY, key="ei_security")
        c4, c5, c6 = st.columns(3)
        c4.selectbox("Requirement clarity", CLARITY, key="ei_clarity")
        c5.selectbox("AI complexity", AI_LEVELS, key="ei_ai")
        c6.checkbox("Native mobile app", key="ei_mobile")

    inputs = _current_inputs(stage.data)
    estimate = calculate_estimate(inputs)
    st.session_state["estimate"] = estimate
    if not _same(inputs, stage.data):
        st.warning("Inputs were adjusted manually and differ from the AI suggestion.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Minimum effort (person-days)", estimate.total_min)
    m2.metric("Maximum effort (person-days)", estimate.total_max)
    m3.metric("Suggested contingency", f"{estimate.contingency_percent}%")
    m4.metric("Overall range (person-days)", f"{estimate.overall_min}-{estimate.overall_max}")

    df = pd.DataFrame(
        [{"Phase": p.phase, "Role": p.role, "Min days": p.min_days, "Max days": p.max_days} for p in estimate.phases]
    ).set_index("Phase")
    st.dataframe(df)
    st.bar_chart(df[["Min days", "Max days"]])

    st.markdown("#### Phase details")
    for p in estimate.phases:
        with st.expander(f"{p.phase}: {p.min_days} - {p.max_days} person-days ({p.role})"):
            st.markdown("**Tasks**")
            for t in p.tasks:
                st.markdown(f"- {t}")
            if p.dependencies:
                st.markdown("**Dependencies**")
                for d in p.dependencies:
                    st.markdown(f"- {d}")
            if p.assumptions:
                st.markdown("**Assumptions**")
                for a in p.assumptions:
                    st.markdown(f"- {a}")

    with st.expander("How this estimate was calculated"):
        st.markdown("**Why these inputs were suggested**")
        for r in stage.data.rationale:
            st.markdown(f"- {r}")
        st.markdown("**Rules applied**")
        for d in estimate.drivers:
            st.markdown(f"- {d}")
        st.caption(f"Subtotal {estimate.total_min} - {estimate.total_max}, plus contingency {estimate.contingency_min} - {estimate.contingency_max}.")

    for note in estimate.disclaimers:
        st.caption(note)