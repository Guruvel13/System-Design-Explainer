import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from io import BytesIO
from kroki_renderer import generate_png_from_dot, generate_pdf_from_dot

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
# USER INPUT
# =============================
st.markdown("### 📝 Describe the System You Want to Design")

requirement = st.text_area(
    "💡 Your system requirement:",
    placeholder="Example: Build a scalable real-time chat application.",
    height=160
)

generate = st.button("✨ Generate Architecture", use_container_width=True)

# =============================
# PROCESS REQUEST
# =============================
if generate:
    if not requirement.strip():
        st.error("⚠️ Please enter a valid requirement.")
    else:
        with st.spinner("⚡ Creating system blueprint..."):
            try:
                raw = call_llm(requirement)

                # Extract structured data
                explanation, nodes, edges, annotations, layers, edge_types = parse_output(raw)

                # =============================
                # EXPLANATION
                # =============================
                st.markdown("## 📘 Architecture Explanation")
                st.markdown(
                    f"""
                    <div style='
                        background-color:#ffffff10;
                        padding:20px;
                        border-radius:12px;
                        border:1px solid #333;
                        color:white;
                        line-height:1.6;
                    '>
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

                    # =============================
                    # DOWNLOAD BUTTON — PNG
                    # =============================
                    try:
                        png_bytes = generate_png_from_dot(graph.source)

                        st.download_button(
                            "📥 Download Architecture (PNG)",
                            png_bytes,
                            "architecture.png",
                            "image/png"
                        )
                    except Exception as e_png:
                        st.error("PNG generation failed.")
                        st.exception(e_png)

                    # =============================
                    # DOWNLOAD BUTTON — PDF
                    # =============================
                    try:
                        pdf_bytes = generate_pdf_from_dot(graph.source)

                        st.download_button(
                            "📄 Download Architecture (PDF)",
                            pdf_bytes,
                            "architecture.pdf",
                            "application/pdf"
                        )
                    except Exception as e_pdf:
                        st.error("PDF generation failed.")
                        st.exception(e_pdf)

                else:
                    st.warning("⚠️ Diagram JSON invalid. Try refining your prompt.")

            except Exception as e:
                st.error("❌ Error generating architecture.")
                st.exception(e)  