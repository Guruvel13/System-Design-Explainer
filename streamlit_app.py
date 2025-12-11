import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from io import BytesIO
import base64

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="SystemSketch AI",
    layout="wide",
    page_icon="🧩"
)

# Import custom CSS
st.markdown("""
<style>
/* Gradient primary button */
.stButton>button {
    background: linear-gradient(90deg, #7b2ff7, #f107a3);
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 0.6rem 1.3rem;
    border: none;
}
.stButton>button:hover {
    opacity: 0.9;
}

/* Floating dark sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161616, #2b2b2b);
    color: white;
}

/* Recolor text inputs for dark mode */
textarea, input, select {
    background-color: #ffffff10 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# =============================
# HEADER
# =============================
st.markdown(
    """
    <div style='text-align:center;'>
        <h1 style='font-size:48px;'>🧩 <b>SystemSketch AI</b></h1>
        <p style='color:gray; font-size:18px;'>
            Generate professional system designs & architecture diagrams instantly  
            Powered by <b>Llama 3.1 — Groq API</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")


# =============================
# SIDEBAR (FLOATING CONTROL PANEL)
# =============================
st.sidebar.title("⚙️ Controls")

# Model selection
model = st.sidebar.selectbox(
    "Choose Model",
    [
        "llama-3.1-8b-instant (Fastest)",
        "llama-3.1-70b-versatile (High Reasoning)",
        "mixtral-8x7b",
        "gemma2-9b"
    ]
)

# Toggle raw JSON
show_json = st.sidebar.checkbox("Show Raw Diagram JSON", value=False)

# Export options
export_md = st.sidebar.checkbox("Enable Markdown Export")
export_ppt = st.sidebar.checkbox("Enable PPT Export")

# Diagram export toggles
export_png = st.sidebar.checkbox("Enable PNG Download")
export_pdf = st.sidebar.checkbox("Enable PDF Download")

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Groq + Streamlit")


# =============================
# INPUT SECTION
# =============================
st.markdown("### 📝 Describe the System You Want to Design")

requirement = st.text_area(
    "💡 Your system requirement:",
    placeholder="Example: Build a scalable real-time chat application supporting millions of users.",
    height=160
)

generate = st.button("✨ Generate Architecture", use_container_width=True)


# =============================
# PROCESS
# =============================
if generate:
    if not requirement.strip():
        st.error("⚠️ Please enter a valid system requirement.")
    else:
        with st.spinner("⚡ Creating system blueprint..."):
            try:
                # Decide model mapping
                model_map = {
                    "llama-3.1-8b-instant (Fastest)": "llama-3.1-8b-instant",
                    "llama-3.1-70b-versatile (High Reasoning)": "llama-3.1-70b-versatile",
                    "mixtral-8x7b": "mixtral-8x7b",
                    "gemma2-9b": "gemma2-9b"
                }

                raw = call_llm(requirement, model_map[model])
                explanation, nodes, edges, annotations = parse_output(raw)

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
                    graph = build_graph(nodes, edges, annotations)
                    st.graphviz_chart(graph)

                    # ---------------------------
                    # EXPORT: PNG
                    # ---------------------------
                    if export_png:
                        png_bytes = graph.pipe(format="png")
                        st.download_button(
                            label="📥 Download Diagram (PNG)",
                            data=png_bytes,
                            file_name="architecture.png",
                            mime="image/png",
                        )

                    # ---------------------------
                    # EXPORT: PDF
                    # ---------------------------
                    if export_pdf:
                        pdf_bytes = graph.pipe(format="pdf")
                        st.download_button(
                            label="📄 Download Diagram (PDF)",
                            data=pdf_bytes,
                            file_name="architecture.pdf",
                            mime="application/pdf",
                        )

                else:
                    st.warning("⚠️ Diagram JSON invalid. Try refining your prompt.")

                # =============================
                # RAW JSON DIAGRAM
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
                # PPT EXPORT
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
