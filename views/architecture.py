"""Architecture Recommendation page."""
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import llm_client
from modules.architecture_generator import PROVIDERS, build_dot, generate_architecture
from modules.common import DemoUnavailableError
from ui_common import show_mode_banner


def _show_mermaid(code: str) -> None:
    """Render Mermaid in the browser. It waits until the frame is visible (tabs start hidden)."""
    html = """
    <div style="background:#ffffff;padding:12px;border-radius:8px;min-height:540px;">
      <pre class="mermaid" id="diagram">__CODE__</pre>
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
      let done = false;
      async function draw() {
        if (done || document.body.clientWidth < 50) return;
        done = true;
        try { await mermaid.run({ querySelector: '#diagram' }); }
        catch (e) { document.getElementById('diagram').textContent = 'Diagram could not be rendered: ' + e; }
      }
      new ResizeObserver(draw).observe(document.body);
      draw();
    </script>
    """.replace("__CODE__", code)
    try:
        st.iframe(html, height=620)
    except (AttributeError, TypeError):  # older Streamlit versions without st.iframe
        components.html(html, height=620, scrolling=True)


def show_diagram(arch) -> None:
    """Mermaid (rendered in the browser) plus a Graphviz backup that always renders."""
    sub1, sub2 = st.tabs(["Mermaid diagram", "Graphviz view (backup)"])
    with sub1:
        _show_mermaid(arch.mermaid_diagram)
        with st.expander("Mermaid source (paste into https://mermaid.live)"):
            st.code(arch.mermaid_diagram, language="text")
    with sub2:
        st.graphviz_chart(build_dot(arch.components))
    st.caption("Dashed boxes are optional components. Dashed arrows show supporting services.")


def _generate(doc_text, extraction, classification, provider: str) -> None:
    try:
        with st.spinner(f"Generating {provider} architecture..."):
            stage = generate_architecture(
                doc_text, extraction.data, classification.data, provider,
                use_demo=st.session_state.get("use_demo", False),
            )
    except DemoUnavailableError as e:
        st.error(str(e))
        return
    except llm_client.LLMError as e:
        st.error(f"The AI service could not generate the architecture: {e}")
        return
    except Exception as e:
        st.error(f"Unexpected error: {type(e).__name__}: {e}")
        return
    st.session_state["architecture"] = stage


def _bullets(items) -> None:
    for item in items:
        st.markdown(f"- {item}")


def render() -> None:
    st.title("Architecture Recommendation")
    extraction = st.session_state.get("extraction")
    classification = st.session_state.get("classification")
    document = st.session_state.get("document")
    if extraction is None or classification is None or document is None:
        st.info("Run the analysis on **Upload Requirements** first.")
        return

    preference = extraction.data.overview.cloud_preferences
    st.caption(f"Cloud preference found in the document: {preference}")
    provider = st.radio("Cloud provider for this draft", list(PROVIDERS), horizontal=True, key="arch_provider")
    if st.button("Generate architecture", type="primary"):
        _generate(document.text, extraction, classification, provider)

    stage = st.session_state.get("architecture")
    if stage is None:
        st.info("Choose a provider and click **Generate architecture**.")
        return

    show_mode_banner()
    arch = stage.data
    if arch.cloud_provider != provider:
        st.caption(f"Showing the {arch.cloud_provider} design. Click Generate to create the {provider} design.")

    st.markdown("#### Assumptions")
    _bullets(arch.assumptions)

    tab1, tab2, tab3, tab4 = st.tabs(["Components", "Diagram", "How it fits together", "Trade-offs and considerations"])
    with tab1:
        df = pd.DataFrame(
            [
                {
                    "Component": c.component_name, "Layer": c.layer, "Suggested service": c.suggested_service,
                    "Status": c.status, "Requirements": ", ".join(c.requirement_ids) or "-",
                }
                for c in arch.components
            ]
        ).set_index("Component")
        st.dataframe(df)
        st.caption("Recommended = justified by the requirements. Optional = useful but not required by them.")
        for c in arch.components:
            with st.expander(f"{c.layer}: {c.component_name} ({c.status})"):
                st.markdown(f"**Suggested service:** {c.suggested_service}")
                st.markdown(f"**Purpose:** {c.purpose}")
                st.markdown(f"**Why:** {c.reason}")
                st.markdown(f"**Considerations:** {c.considerations or 'None noted'}")
                st.markdown(f"**Related requirements:** {', '.join(c.requirement_ids) or 'None'}")
    with tab2:
        show_diagram(arch)
    with tab3:
        st.write(arch.communication_flow)
    with tab4:
        st.markdown("**Key trade-offs**")
        _bullets(arch.trade_offs)
        st.markdown("**Security considerations**")
        _bullets(arch.security_considerations)
        st.markdown("**Scalability considerations**")
        _bullets(arch.scalability_considerations)
    st.caption("No cost estimate is given: cloud costs need workload data and current pricing.")