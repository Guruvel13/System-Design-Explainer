import os
import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph

# ------------------- Page Setup ------------------- #
st.set_page_config(
    page_title="System Design Explainer",
    layout="wide"
)

st.title("System Design Explainer")
st.caption("Powered by Llama 3 (Free via Groq API)")
st.markdown("---")

# ------------------- Debug: Check if API Key Loaded ------------------- #
st.subheader("Debug Info")
st.write("GROQ KEY LOADED:", os.getenv("GROQ_API_KEY") is not None)
st.markdown("---")

# ------------------- User Input ------------------- #
st.subheader("Enter Your Requirement")
requirement = st.text_area(
    "Describe the system you want to design:",
    "Design a scalable real-time chat application with millions of daily active users.",
    height=160
)

generate = st.button("Generate System Design", use_container_width=True)

# ------------------- System Design Generation ------------------- #
if generate:
    if not requirement.strip():
        st.error("Please enter a valid requirement.")
    else:
        with st.spinner("Generating system design using Llama 3…"):
            try:
                raw = call_llm(requirement)
                explanation, nodes, edges = parse_output(raw)

                st.markdown("---")
                st.subheader("System Design Explanation")
                st.write(explanation)

                # ------------------- Diagram ------------------- #
                if nodes and edges:
                    st.subheader("Generated Architecture Diagram")
                    graph = build_graph(nodes, edges)
                    st.graphviz_chart(graph)
                else:
                    st.warning("The model did not return valid diagram JSON.")

                # ------------------- Raw Output ------------------- #
                with st.expander("Show Raw Model Output"):
                    st.text(raw)

            except Exception as e:
                st.error("Error generating system design.")
                st.exception(e)
