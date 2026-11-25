"""Small helpers shared by the Streamlit views."""
import streamlit as st

import config

REVIEW_NOTICE = (
    "AI-generated draft for human review. A solution architect must verify the requirements, architecture and "
    "estimates before anything is shared with a customer. Estimates are preliminary and are not a quotation."
)

# Results that carry a .mode ("AI" or "DEMO")
STAGE_KEYS = ("extraction", "clarification", "classification", "risks", "architecture", "effort_inputs", "roadmap")
# Other results stored in session state
EXTRA_KEYS = ("estimate",)


def init_state() -> None:
    """Create the session-state slots the app uses (only fills missing ones)."""
    st.session_state.setdefault("document", None)
    st.session_state.setdefault("doc_key", None)
    for key in STAGE_KEYS + EXTRA_KEYS:
        st.session_state.setdefault(key, None)
    st.session_state.setdefault("use_demo", not config.has_api_key())
    st.session_state.setdefault("nav", "Dashboard")
    st.session_state.setdefault("pipeline_error", None)


def reset_results() -> None:
    for key in STAGE_KEYS + EXTRA_KEYS:
        st.session_state[key] = None
    for key in [k for k in st.session_state.keys() if str(k).startswith("ei_")]:
        del st.session_state[key]  # estimate what-if widgets


def go_to(page: str) -> None:
    """Button callback: switch the sidebar page."""
    st.session_state["nav"] = page


def show_mode_banner() -> None:
    """Always tell the user whether results came from the live AI or from demo data."""
    stages = [st.session_state.get(k) for k in STAGE_KEYS]
    stages = [s for s in stages if s is not None]
    if not stages:
        return
    if any(s.mode == "DEMO" for s in stages):
        st.warning("**DEMO MODE** - this output comes from built-in sample data, not from a live AI model.")
        for notice in sorted({s.notice for s in stages if s.notice}):
            st.caption(notice)
    else:
        st.info(REVIEW_NOTICE)