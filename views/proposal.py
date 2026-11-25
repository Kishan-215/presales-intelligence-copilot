"""Proposal Generator page: preview and download the proposal draft as Markdown."""
import streamlit as st

import config
from modules.pipeline import FULL_KEYS
from modules.proposal_generator import generate_proposal
from ui_common import show_mode_banner
from views.architecture import show_diagram


def render() -> None:
    st.title("Proposal Generator")
    results = {key: st.session_state.get(key) for key in FULL_KEYS}
    if results["extraction"] is None:
        st.info("Run the analysis on **Upload Requirements** first.")
        return

    missing = [key for key in FULL_KEYS if results[key] is None]
    if missing:
        st.warning(f"Some stages have no result yet ({', '.join(missing)}). Those sections will show as not generated.")
    show_mode_banner()

    markdown = generate_proposal(results)
    name = results["extraction"].data.overview.project_name
    st.subheader(name)

    c1, c2, _ = st.columns([1, 1, 2])
    c1.download_button("Download proposal (Markdown)", data=markdown, file_name="proposal_draft.md", mime="text/markdown")
    if c2.button("Save copy to outputs folder"):
        try:
            out_dir = config.BASE_DIR / "outputs"
            out_dir.mkdir(exist_ok=True)
            (out_dir / "proposal_draft.md").write_text(markdown, encoding="utf-8")
            st.success(f"Saved to {out_dir / 'proposal_draft.md'}")
        except OSError as e:
            st.error(f"Could not save the file: {e}")

    tab1, tab2, tab3 = st.tabs(["Preview", "Architecture diagram", "Markdown source"])
    with tab1:
        st.markdown(markdown)
    with tab2:
        arch = results["architecture"]
        if arch is not None:
                        show_diagram(arch.data)
        else:
            st.info("No architecture has been generated yet.")
    with tab3:
        st.code(markdown, language="markdown")