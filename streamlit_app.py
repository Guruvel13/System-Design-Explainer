# streamlit_app.py
import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from kroki_renderer import generate_svg_from_dot, generate_png_from_dot, generate_pdf_from_dot
from io import BytesIO

st.set_page_config(page_title="SystemSketch AI", layout="wide", page_icon="🧩")

st.markdown("""
<div style='text-align:center;'>
    <h1 style='font-size:48px;'>🧩 <b>SystemSketch AI</b></h1>
    <p style='color:gray; font-size:18px;'>
        Generate professional system designs & architecture diagrams instantly<br>
        Powered by <b>Llama 3.1 — Groq API</b>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📝 Describe the System You Want to Design")

requirement = st.text_area(
    "💡 Your system requirement:",
    placeholder="Example: Build a scalable ride-hailing system.",
    height=160
)

generate = st.button("✨ Generate Architecture", use_container_width=True)

if generate:
    if not requirement.strip():
        st.error("⚠️ Please enter a valid system requirement.")
    else:
        with st.spinner("⚡ Creating system blueprint..."):
            try:
                raw = call_llm(requirement)
                explanation, nodes, edges, annotations, layers, edge_types = parse_output(raw)

                st.markdown("## 📘 Architecture Explanation")
                st.write(explanation)

                st.markdown("## 🗺 Architecture Diagram")

                if nodes and edges:
                    dot = build_graph(nodes, edges, annotations, layers, edge_types)

                    svg = generate_svg_from_dot(dot.source)
                    st.image(svg)

                    col1, col2 = st.columns(2)

                    with col1:
                        png = generate_png_from_dot(dot.source)
                        st.download_button("📥 Download PNG", png, "architecture.png", "image/png")

                    with col2:
                        pdf = generate_pdf_from_dot(dot.source)
                        st.download_button("📄 Download PDF", pdf, "architecture.pdf", "application/pdf")

                else:
                    st.warning("⚠️ Diagram JSON invalid. Try refining your prompt.")

            except Exception as e:
                st.error("❌ Error generating architecture.")
                st.exception(e)
