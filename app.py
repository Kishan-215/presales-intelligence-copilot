import streamlit as st

import config
from ui_common import init_state, reset_results
from views import about, analysis, architecture, dashboard, effort, proposal, roadmap, upload

st.set_page_config(page_title=config.APP_NAME, page_icon="📋", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.25);
        padding: 12px 16px;
        border-radius: 10px;
    }
    .block-container {padding-top: 2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

PAGES = {
    "Dashboard": dashboard.render,
    "Upload Requirements": upload.render,
    "Requirement Analysis": analysis.render,
    "Architecture Recommendation": architecture.render,
    "Effort Estimation": effort.render,
    "Technical Roadmap": roadmap.render,
    "Proposal Generator": proposal.render,
    "About Project": about.render,
}

with st.sidebar:
    st.markdown(f"### 📋 {config.APP_NAME}")
    st.caption(config.APP_SUBTITLE)
    page = st.radio("Navigation", list(PAGES.keys()), key="nav", label_visibility="collapsed")
    st.divider()
    if config.has_api_key():
        st.success(f"API key configured\n\nModel: {config.LLM_MODEL}")
    else:
        st.warning("No API key configured. Demo mode only (sample RFP).")
    if st.button("Clear results"):
        reset_results()
        st.rerun()
    st.caption("AI-generated drafts need human architect review.")

PAGES[page]()