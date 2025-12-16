# streamlit_app.py
import streamlit as st
from llm_client import call_llm
from diagram_parser import parse_output
from diagram_builder import build_graph
from kroki_renderer import generate_png_from_dot, generate_pdf_from_dot

st.set_page_config(
    page_title="SystemSketch AI - AI-Powered Architecture Generator", 
    layout="wide", 
    page_icon="🧩",
    initial_sidebar_state="collapsed"
)

# Premium Modern Design System
st.markdown("""
<style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main App Background with Gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        background-attachment: fixed;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }
    
    /* Hero Header with Glassmorphism */
    .hero-header {
        text-align: center;
        padding: 3rem 2rem;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 3rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: fadeInDown 0.8s ease-out;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    .hero-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    /* Input Section Card */
    .input-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .input-card:hover {
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .section-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Textarea Styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Premium Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: 16px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
        letter-spacing: 0.02em !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Download Buttons */
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(102, 126, 234, 0.4) !important;
        color: white !important;
        padding: 0.875rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.7) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Explanation Card */
    .explanation-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.8;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .explanation-card h1, .explanation-card h2, .explanation-card h3 {
        color: rgba(255, 255, 255, 0.95);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .explanation-card p {
        margin-bottom: 1rem;
        color: rgba(255, 255, 255, 0.85);
    }
    
    .explanation-card ul, .explanation-card ol {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .explanation-card li {
        margin-bottom: 0.5rem;
        color: rgba(255, 255, 255, 0.85);
    }
    
    /* Diagram Card */
    .diagram-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Warning/Error Styling */
    .warning-card {
        background: rgba(251, 191, 36, 0.1);
        border: 2px solid rgba(251, 191, 36, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        color: #fbbf24;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: shake 0.5s ease;
    }
    
    /* Spinner Customization */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
    }
    
    /* Code Block */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes shimmer {
        0%, 100% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Stats Badge */
    .stats-badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        color: #a5b4fc;
        margin: 0.25rem;
    }
    
    /* Graphviz Chart Container */
    .stGraphVizChart {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        border-radius: 12px !important;
        color: #4ade80 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
        color: #f87171 !important;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        border-radius: 12px !important;
        color: #fbbf24 !important;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class='hero-header'>
    <div class='hero-icon'>🧩</div>
    <h1 class='hero-title'>SystemSketch AI</h1>
    <p class='hero-subtitle'>Transform your ideas into comprehensive system architectures with AI-powered intelligence</p>
    <div style='margin-top: 1.5rem;'>
        <span class='stats-badge'>⚡ Powered by Llama 3.1</span>
        <span class='stats-badge'>🎨 Instant Visualization</span>
        <span class='stats-badge'>📊 Export Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Input Section
st.markdown("""
<div class='section-label'>
    💭 Describe Your System Requirements
</div>
""", unsafe_allow_html=True)

req = st.text_area(
    "",
    placeholder="Example: Design a scalable real-time chat application supporting 1M concurrent users with end-to-end encryption, presence indicators, and message history...",
    height=160,
    key="requirement_input"
)

generate = st.button("✨ Generate Architecture", use_container_width=True)

if generate:
    if not req.strip():
        st.error("⚠️ Please enter a system requirement to generate architecture.")
    else:
        with st.spinner("🤖 AI is crafting your architecture..."):
            try:
                raw = call_llm(req)
                explanation, nodes, edges, annotations, layers, edge_types = parse_output(raw)

                # Explanation Section
                st.markdown("""
                <div class='section-header'>
                    📘 Architecture Explanation
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='explanation-card'>
                    {explanation}
                </div>
                """, unsafe_allow_html=True)

                # Diagram Section
                st.markdown("""
                <div class='section-header'>
                    🗺️ Architecture Diagram
                </div>
                """, unsafe_allow_html=True)
                
                if nodes and edges:
                    st.markdown("<div class='diagram-card'>", unsafe_allow_html=True)
                    graph = build_graph(nodes, edges, annotations=annotations, layers=layers, edge_types=edge_types, dark_mode=True)
                    st.graphviz_chart(graph, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Download Section
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div class='section-label'>
                        📥 Export Your Diagram
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        svg_src = graph.source
                        png_bytes = generate_png_from_dot(svg_src)
                        pdf_bytes = generate_pdf_from_dot(svg_src)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📥 Download PNG",
                                png_bytes,
                                "architecture_diagram.png",
                                "image/png",
                                use_container_width=True
                            )
                        with col2:
                            st.download_button(
                                "📄 Download PDF",
                                pdf_bytes,
                                "architecture_diagram.pdf",
                                "application/pdf",
                                use_container_width=True
                            )

                    except Exception as e:
                        st.warning("⚠️ Export service temporarily unavailable. You can still view and use the diagram above.")
                        with st.expander("🔍 View Error Details"):
                            st.exception(e)
                else:
                    st.markdown("""
                    <div class='warning-card'>
                        ⚠️ Unable to generate diagram from the AI response. Please try refining your prompt or try again.
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("🔍 Show Raw AI Output"):
                        st.code(raw, language="text")

            except Exception as e:
                st.error("❌ An error occurred while generating the architecture. Please try again.")
                with st.expander("🔍 View Error Details"):
                    st.exception(e)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.4); font-size: 0.875rem; padding: 2rem 0;'>
    Built with ❤️ using Groq AI, Llama 3.1, and Streamlit
</div>
""", unsafe_allow_html=True)
