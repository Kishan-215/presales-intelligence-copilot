"""Upload Requirements page: load a document, parse it, run the analysis pipeline."""
import streamlit as st

import config
import llm_client
from modules.clarification_generator import generate_clarifications
from modules.common import DemoUnavailableError
from modules.demo_data import SAMPLE_RFP_PATH, is_sample_document
from modules.document_parser import DocumentParseError, parse_pasted_text, parse_uploaded_file
from modules.project_classifier import classify_project
from modules.requirement_extractor import extract_requirements
from ui_common import go_to, reset_results, show_mode_banner
from modules.pipeline import FULL_KEYS, run_full_analysis


def _store_document(doc, key: str) -> None:
    st.session_state["document"] = doc
    st.session_state["doc_key"] = key
    reset_results()  # a new document invalidates old results


def _clear_document() -> None:
    st.session_state["document"] = None
    st.session_state["doc_key"] = None


def _upload_input() -> None:
    up = st.file_uploader(f"PDF or TXT file (max {config.MAX_UPLOAD_MB} MB)", type=["pdf", "txt"])
    if up is None:
        return
    key = f"file:{up.name}:{up.size}"
    if st.session_state["doc_key"] == key:
        return  # already parsed
    try:
        _store_document(parse_uploaded_file(up.name, up.getvalue()), key)
    except DocumentParseError as e:
        _clear_document()
        st.error(str(e))
    except Exception as e:  # never crash the app on a bad file
        _clear_document()
        st.error(f"Unexpected error while reading the file: {type(e).__name__}: {e}")


def _paste_input() -> None:
    text = st.text_area("Paste the customer requirements here", height=220, key="paste_text")
    if st.button("Use this text"):
        try:
            _store_document(parse_pasted_text(text), "pasted")
        except DocumentParseError as e:
            _clear_document()
            st.error(str(e))


def _sample_input() -> None:
    st.caption("A synthetic healthcare RFP created for demonstration. It is not a real customer document.")
    if st.button("Load sample RFP"):
        try:
            _store_document(parse_uploaded_file("sample_rfp.txt", SAMPLE_RFP_PATH.read_bytes()), "sample")
        except (DocumentParseError, OSError) as e:
            _clear_document()
            st.error(f"Could not load the sample RFP: {e}")


def _show_document(doc) -> None:
    st.subheader("Loaded document")
    st.markdown(f"**File:** {doc.filename}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Type", doc.source_type.upper())
    c2.metric("Pages", doc.page_count if doc.page_count else "n/a")
    c3.metric("Characters", f"{doc.char_count:,}")
    for warning in doc.warnings:
        st.warning(warning)
    with st.expander("Preview extracted text"):
        st.text(doc.text[:5000])
        if doc.char_count > 5000:
            st.caption(f"Showing the first 5,000 of {doc.char_count:,} characters.")


def _run_pipeline(text: str, use_demo: bool, resume: bool) -> None:
    st.session_state["pipeline_error"] = None
    if not resume:
        reset_results()
    results = {key: st.session_state.get(key) for key in FULL_KEYS}
    error = None
    try:
        with st.status("Running analysis...", expanded=True) as status:
            run_full_analysis(text, use_demo=use_demo, on_step=st.write, results=results)
            status.update(label="Analysis complete", state="complete", expanded=False)
    except DemoUnavailableError as e:
        error = str(e)
    except llm_client.LLMError as e:
        error = f"The AI service could not finish the analysis: {e}"
    except Exception as e:
        error = f"Unexpected error: {type(e).__name__}: {e}"
    for key, value in results.items():  # keep every stage that finished
        if value is not None:
            st.session_state[key] = value
    if error:
        st.session_state["pipeline_error"] = error
        st.rerun()


def _analysis_controls(doc) -> None:
    st.divider()
    st.subheader("Run analysis")
    if not config.has_api_key():
        st.info("No API key is configured, so only demo mode is available (sample RFP only).")
    use_demo = st.checkbox(
        "Demo mode (built-in sample output, no AI call)",
        value=st.session_state.get("use_demo", False),
        help="Works only with the built-in sample RFP. Results are clearly labeled as demo data.",
    )
    st.session_state["use_demo"] = use_demo
    if use_demo and not is_sample_document(doc.text):
        st.warning("Demo mode only works with the sample RFP. Untick it to analyse this document with the AI.")

    if st.session_state.get("pipeline_error"):
        st.error(st.session_state["pipeline_error"])
        st.caption("Stages that finished are kept. Use Continue to retry only the remaining stages.")

    done = [key for key in FULL_KEYS if st.session_state.get(key) is not None]
    partial = 0 < len(done) < len(FULL_KEYS)
    c1, c2, _ = st.columns([1, 2, 3])
    if c1.button("Run analysis", type="primary"):
        _run_pipeline(doc.text, use_demo, resume=False)
    if partial and c2.button("Continue (keep finished stages)"):
        _run_pipeline(doc.text, use_demo, resume=True)

    if all(st.session_state.get(key) is not None for key in FULL_KEYS):
        show_mode_banner()
        ss = st.session_state
        st.success(
            f"Analysis complete: {len(ss['extraction'].data.requirements)} requirements, "
            f"{len(ss['clarification'].data.questions)} questions, {len(ss['risks'].data.risks)} risks, "
            f"{ss['estimate'].overall_min}-{ss['estimate'].overall_max} person-days (preliminary), "
            f"{len(ss['roadmap'].data.phases)} roadmap phases."
        )
        st.button("View requirement analysis →", on_click=go_to, args=("Requirement Analysis",))


def render() -> None:
    st.title("Upload Requirements")
    st.caption(
        "Provide a customer RFP, brief, email or meeting notes. PDF and TXT files are supported. "
        "Scanned PDFs are not supported in this MVP (no OCR)."
    )
    method = st.radio(
        "Input method",
        ["Upload a file", "Paste text", "Use the built-in sample RFP"],
        horizontal=True,
    )
    if method == "Upload a file":
        _upload_input()
    elif method == "Paste text":
        _paste_input()
    else:
        _sample_input()

    doc = st.session_state.get("document")
    if doc is None:
        st.info("No document loaded yet.")
        return
    _show_document(doc)
    _analysis_controls(doc)