import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph

# ------------------- Page Setup ------------------- #
st.set_page_config(
    page_title="System Design Explainer",
    layout="wide"
)

# ------------------- Header ------------------- #
st.title("System Design Explainer")
st.caption("Powered by Llama 3.1 8B Instant — via Groq API")
st.markdown("---")

# ------------------- User Input ------------------- #
st.subheader("Describe the System You Want to Design")
requirement = st.text_area(
    "",
    "Design a scalable real-time chat application with millions of daily active users.",
    height=150,
    placeholder="Enter any system requirement. Example: Build an e-commerce platform handling 1M daily users."
)

generate = st.button("Generate Architecture", use_container_width=True)

# ------------------- System Design Generation ------------------- #
if generate:
    if not requirement.strip():
        st.error("Please enter a valid requirement.")
    else:
        with st.spinner("Generating system design…"):
            try:
                raw = call_llm(requirement)
                explanation, nodes, edges = parse_output(raw)

                # Explanation Section
                st.markdown("---")
                st.subheader("Architecture Explanation")
                st.write(explanation)

                # Diagram Section
                st.markdown("---")
                if nodes and edges:
                    st.subheader("Generated Architecture Diagram")
                    graph = build_graph(nodes, edges)
                    st.graphviz_chart(graph)
                else:
                    st.warning("The model did not return valid diagram JSON. Try rewriting your prompt.")

            except Exception as e:
                st.error("An error occurred while generating the system design.")
                st.exception(e)
