import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from io import BytesIO

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="SystemSketch AI",
    layout="wide",
    page_icon="🧩"
)

# =============================
# HEADER
# =============================
st.markdown(
    """
    <div style='text-align:center;'>
        <h1 style='font-size:48px;'>🧩 <b>SystemSketch AI</b></h1>
        <p style='color:gray; font-size:18px;'>
            Generate professional system designs & architecture diagrams instantly<br>
            Powered by <b>Llama 3.1 — Groq API</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")


# =============================
# SIDEBAR CONTROLS
# =============================
st.sidebar.title("⚙️ Options")

show_json = st.sidebar.checkbox("Show Raw Diagram JSON", value=False)
export_md = st.sidebar.checkbox("Enable Markdown Export")
export_ppt = st.sidebar.checkbox("Enable PPT Export")
export_png = st.sidebar.checkbox("Enable PNG Download")
export_pdf = st.sidebar.checkbox("Enable PDF Download")

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Groq + Streamlit")


# =============================
# USER INPUT
# =============================
st.markdown("### 📝 Describe the System You Want to Design")

requirement = st.text_area(
    "💡 Your system requirement:",
    placeholder="Example: Build a scalable real-time chat application supporting millions of users.",
    height=160
)

generate = st.button("✨ Generate Architecture", use_container_width=True)


# =============================
# PROCESS REQUEST
# =============================
if generate:
    if not requirement.strip():
        st.error("⚠️ Please enter a valid system requirement.")
    else:
        with st.spinner("⚡ Creating system blueprint..."):
            try:
                # Always uses llama-3.1-8b-instant
                raw = call_llm(requirement)

                explanation, nodes, edges, annotations, layers, edge_types = parse_output(raw)

                # =============================
                # EXPLANATION
                # =============================
                st.markdown("## 📘 Architecture Explanation")
                st.markdown(
                    f"""
                    <div style="
                        background-color:#ffffff10;
                        padding:20px;
                        border-radius:12px;
                        border:1px solid #333;
                        color:white;
                        line-height:1.6;
                    ">
                        {explanation}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # =============================
                # DIAGRAM
                # =============================
                st.markdown("## 🗺 Architecture Diagram")

                if nodes and edges:
                    graph = build_graph(
                        nodes,
                        edges,
                        annotations=annotations,
                        layers=layers,
                        edge_types=edge_types,
                        dark_mode=True
                    )
                    st.graphviz_chart(graph)

                    # ---------------------------
                    # EXPORT: PNG
                    # ---------------------------
                    if export_png:
                        png_bytes = graph.pipe(format="png")
                        st.download_button(
                            "📥 Download Diagram (PNG)",
                            png_bytes,
                            "architecture.png",
                            "image/png",
                        )

                    # ---------------------------
                    # EXPORT: PDF
                    # ---------------------------
                    if export_pdf:
                        pdf_bytes = graph.pipe(format="pdf")
                        st.download_button(
                            "📄 Download Diagram (PDF)",
                            pdf_bytes,
                            "architecture.pdf",
                            "application/pdf",
                        )

                else:
                    st.warning("⚠️ Diagram JSON invalid. Try refining your prompt.")

                # =============================
                # RAW JSON OUTPUT
                # =============================
                if show_json:
                    st.markdown("### 🧾 Raw Diagram JSON")
                    st.code(raw, language="json")

                # =============================
                # MARKDOWN EXPORT
                # =============================
                if export_md:
                    md_export = f"# System Architecture Explanation\n\n{explanation}"
                    st.download_button(
                        "📄 Download Explanation (Markdown)",
                        md_export,
                        "architecture.md"
                    )

                # =============================
                # PPT EXPORT (text-only placeholder)
                # =============================
                if export_ppt:
                    ppt_bytes = BytesIO()
                    ppt_bytes.write(explanation.encode("utf-8"))
                    st.download_button(
                        "📊 Download Explanation (PPT Placeholder)",
                        ppt_bytes.getvalue(),
                        "architecture.pptx"
                    )

            except Exception as e:
                st.error("❌ Error generating architecture.")
                st.exception(e)
