import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from io import BytesIO
from kroki_renderer import generate_svg_from_dot, generate_png_from_dot, generate_pdf_from_dot

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
                raw = call_llm(requirement)

                # Parse all values
                explanation, nodes, edges, annotations, layers, edge_types = parse_output(raw)

                # =============================
                # EXPLANATION SECTION
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
                # DIAGRAM SECTION
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

                    # Render interactive diagram in Streamlit UI
                    st.graphviz_chart(graph)

                    # ----------------------------
                    # SVG Export via Kroki (recommended)
                    # ----------------------------
                    try:
                        svg_bytes = generate_svg_from_dot(graph.source)
                        st.download_button(
                            "📥 Download Diagram (SVG)",
                            svg_bytes,
                            "architecture.svg",
                            "image/svg+xml"
                        )
                    except Exception as ex_svg:
                        st.warning("SVG export failed (Kroki). You can still copy diagram source or try again.")
                        st.exception(ex_svg)

                    # ----------------------------
                    # PNG Export (on-demand)
                    # ----------------------------
                    if st.button("📥 Generate & Download PNG"):
                        try:
                            png_bytes = generate_png_from_dot(graph.source)
                            st.download_button(
                                "Download PNG now",
                                png_bytes,
                                "architecture.png",
                                "image/png"
                            )
                        except Exception as ex_png:
                            st.error("PNG generation failed (Kroki).")
                            st.exception(ex_png)

                    # ----------------------------
                    # PDF Export (on-demand)
                    # ----------------------------
                    if st.button("📄 Generate & Download PDF"):
                        try:
                            pdf_bytes = generate_pdf_from_dot(graph.source)
                            st.download_button(
                                "Download PDF now",
                                pdf_bytes,
                                "architecture.pdf",
                                "application/pdf"
                            )
                        except Exception as ex_pdf:
                            st.error("PDF generation failed (Kroki).")
                            st.exception(ex_pdf)

                    # =============================
                    # DOWNLOAD: Explanation MD
                    # =============================
                    md_text = f"# System Architecture Explanation\n\n{explanation}"
                    st.download_button(
                        "📄 Download Explanation (Markdown)",
                        md_text,
                        "architecture.md"
                    )

                    # =============================
                    # DOWNLOAD: PPT (placeholder text only)
                    # =============================
                    ppt_bytes = BytesIO()
                    ppt_bytes.write(explanation.encode("utf-8"))
                    st.download_button(
                        "📊 Download Explanation (PPT)",
                        ppt_bytes.getvalue(),
                        "architecture.pptx"
                    )

                else:
                    st.warning("⚠️ Diagram JSON invalid. Try refining your prompt.")

            except Exception as e:
                st.error("❌ Error generating architecture.")
                st.exception(e)
