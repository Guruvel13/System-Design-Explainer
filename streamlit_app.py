# streamlit_app.py
import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from kroki_renderer import generate_png_from_dot, generate_pdf_from_dot

st.set_page_config(page_title="SystemSketch AI", layout="wide", page_icon="🧩")

# Simple style
st.markdown("""
<style>
body { background-color: #0b0b0b; color: #eaeaea; }
.section { padding: 12px; border-radius: 10px; margin-bottom: 12px; }
.header { text-align:center; margin-bottom: 8px; }
.explain { background:#141414; padding:18px; border-radius:10px; }
.warn { background:#4b4b1f; padding:12px; border-radius:8px; color:#fff; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>🧩 SystemSketch AI</h1><p>Generate architecture explanation & diagram</p></div>", unsafe_allow_html=True)
st.markdown("---")

st.subheader("Enter system requirement")
req = st.text_area("", placeholder="Example: Design a scalable real-time chat supporting 1M concurrent users", height=140)
generate = st.button("✨ Generate Architecture")

if generate:
    if not req.strip():
        st.error("Please enter a requirement.")
    else:
        with st.spinner("Calling LLM and building diagram..."):
            try:
                raw = call_llm(req)
                explanation, nodes, edges, annotations, layers, edge_types = parse_output(raw)

                # Explanation
                st.markdown("## 📘 Architecture Explanation")
                st.markdown(f"<div class='explain'>{explanation}</div>", unsafe_allow_html=True)

                # Diagram
                st.markdown("## 🗺 Architecture Diagram")
                if nodes and edges:
                    graph = build_graph(nodes, edges, annotations=annotations, layers=layers, edge_types=edge_types, dark_mode=True)
                    st.graphviz_chart(graph)

                    # Provide two download buttons: PNG and PDF
                    try:
                        svg_src = graph.source  # dot source
                        png_bytes = generate_png_from_dot(svg_src)
                        pdf_bytes = generate_pdf_from_dot(svg_src)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button("📥 Download PNG", png_bytes, "architecture.png", "image/png")
                        with col2:
                            st.download_button("📄 Download PDF", pdf_bytes, "architecture.pdf", "application/pdf")

                    except Exception as e:
                        st.warning("Export failed (Kroki). You can still copy raw output or retry.")
                        st.exception(e)
                else:
                    st.markdown("<div class='warn'>⚠️ Diagram JSON invalid. Try refining your prompt.</div>", unsafe_allow_html=True)
                    with st.expander("Show raw model output"):
                        st.code(raw)

            except Exception as e:
                st.error("Error generating architecture.")
                st.exception(e)
