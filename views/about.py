"""About page."""
import streamlit as st

import config


def render() -> None:
    st.title("About Project")
    st.markdown(
        f"""
**{config.APP_NAME}** . It turns a customer requirements document
(RFP, brief, email or notes) into a structured presales draft: requirements, clarification questions,
project classification, architecture recommendation, effort estimate, risks and a technical roadmap.

**Workflow:** document upload -> text extraction -> AI requirement extraction -> clarification questions
-> classification -> architecture -> effort estimate -> risks -> roadmap -> proposal report.

**How it works**
- PDF/TXT text is extracted locally (PyMuPDF).
- A large language model returns structured JSON, which is validated with Pydantic before it is used.
- Effort totals and contingency are calculated with deterministic Python rules, not by the AI.
- Every extracted requirement carries a source excerpt, and excerpts that cannot be found in the document are flagged.
- Demo mode uses built-in sample output, works only with the sample RFP, and is always labeled.

**Important limitations**
- Output is an AI-generated draft and must be reviewed by a solution architect.
- Estimates are preliminary, assumption-based and not calibrated against any company's delivery history.
- The sample RFP is synthetic. It is not a real customer document.
- Scanned PDFs (images) are not supported because the MVP has no OCR.
"""
    )