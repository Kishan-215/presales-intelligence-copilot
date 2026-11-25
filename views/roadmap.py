"""Technical Roadmap page."""
import pandas as pd
import streamlit as st

from modules.roadmap_generator import missing_phases
from ui_common import show_mode_banner


def _bullets(items) -> None:
    for item in items:
        st.markdown(f"- {item}")


def render() -> None:
    st.title("Technical Roadmap")
    stage = st.session_state.get("roadmap")
    if stage is None:
        st.info("Run the analysis on **Upload Requirements** first.")
        return
    show_mode_banner()
    roadmap = stage.data

    missing = missing_phases(roadmap)
    if missing:
        st.warning("The roadmap does not clearly cover: " + ", ".join(missing))
    if roadmap.notes:
        st.info(roadmap.notes)

    df = pd.DataFrame(
        [{"Phase": p.phase_name, "Estimated duration": p.estimated_duration} for p in roadmap.phases]
    ).set_index("Phase")
    st.dataframe(df)

    for p in roadmap.phases:
        with st.expander(p.phase_name):
            st.markdown(f"**Estimated duration:** {p.estimated_duration}")
            st.markdown("**Activities**")
            _bullets(p.activities)
            st.markdown("**Deliverables**")
            _bullets(p.deliverables)
            st.markdown("**Dependencies**")
            _bullets(p.dependencies)
            st.markdown("**Completion criteria**")
            _bullets(p.completion_criteria)
    st.caption("Durations are indicative ranges. No delivery dates are promised without a team size, working calendar and agreed scope.")