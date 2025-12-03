import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph

st.title("System Design Explainer (Gemma-2-2B-IT – Free Model)")

requirement = st.text_area(
    "Enter requirement:",
    "Design a scalable real-time chat application."
)

if st.button("Generate"):
    with st.spinner("Calling LLM…"):
        raw = call_llm(requirement)
        explanation, nodes, edges = parse_output(raw)

    st.subheader("Explanation")
    st.write(explanation)

    if nodes and edges:
        st.subheader("Diagram")
        graph = build_graph(nodes, edges)
        st.graphviz_chart(graph)
    else:
        st.warning("Diagram JSON missing or invalid.")

    st.subheader("Raw Output")
    st.text(raw)
    
if not response.ok:
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    raise RuntimeError("HF API error")
