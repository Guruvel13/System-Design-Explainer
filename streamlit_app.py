import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph

# ------------------- Page Setup ------------------- #
st.set_page_config(
    page_title="SystemSketch AI",
    layout="wide",
    page_icon="🧩"
)

# ------------------- Header ------------------- #
st.markdown("<h1 style='text-align: center;'>🧩 SystemSketch AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>⚡ Powered by Llama 3.1 8B Instant — via Groq API</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------- User Input ------------------- #
st.subheader("📝 Describe the System You Want to Design")

requirement = st.text_area(
    "💡 Enter your system requirement:",
    placeholder="Example: Build a scalable real-time chat application supporting millions of users.",
    height=150
)

generate = st.button("✨ Generate Architecture", use_container_width=True)

# ------------------- System Design Generation ------------------- #
if generate:
    if not requirement.strip():
        st.error("⚠️ Please enter a valid requirement.")
    else:
        with st.spinner("⚡ Generating system design..."):
            try:
                raw = call_llm(requirement)
                explanation, nodes, edges = parse_output(raw)

                # Explanation
                st.markdown("---")
                st.subheader("📘 Architecture Explanation")
                st.write(explanation)

                # Diagram
                st.markdown("---")
                if nodes and edges:
                    st.subheader("🗺 Generated Architecture Diagram")
                    graph = build_graph(nodes, edges)
                    st.graphviz_chart(graph)
                else:
                    st.warning("⚠️ The model did not return valid diagram JSON. Try refining your prompt.")

            except Exception as e:
                st.error("❌ An error occurred while generating the system design.")
                st.exception(e)
                st.info("💡 Tip: Ensure your requirement is clear and specific.")
                