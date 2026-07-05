"""Main Streamlit application for DocIntel."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from app.ingestion.pipeline import IngestionPipeline
from app.agents.orchestrator import DocumentAgent
import tempfile
from datetime import datetime
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="DocIntel - Document Intelligence Platform",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
        text-shadow: none;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #4a4a5a;
        margin-bottom: 2rem;
        font-weight: 300;
        opacity: 0.9;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Chat Messages */
    .stChatMessage {
        border-radius: 16px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
        transition: all 0.3s ease !important;
        animation: fadeInUp 0.5s ease-out !important;
    }
    
    .stChatMessage:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
        transform: translateY(-2px);
    }
    
    /* User Message */
    .chat-message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 16px 16px 4px 16px !important;
    }
    
    /* Assistant Message */
    .chat-message-assistant {
        background: white !important;
        border: 1px solid #e8e8e8 !important;
        border-radius: 16px 16px 16px 4px !important;
    }
    
    /* Source Box */
    .source-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #667eea;
        padding: 14px 16px;
        margin: 10px 0;
        border-radius: 8px;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #667eea, #764ba2) 1;
    }
    
    .source-box:hover {
        background: linear-gradient(135deg, #f0f2f6 0%, #e0e4ea 100%);
        transform: translateX(4px);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 20px 24px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        border: 1px solid rgba(102, 126, 234, 0.15);
        margin: 10px 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        background: rgba(255,255,255,0.9);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.10);
        border-color: #667eea;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-right: 1px solid rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.96) !important;
    }
    
    /* File Uploader */
    .uploadedFile {
        border: 2px dashed #667eea !important;
        border-radius: 12px !important;
        padding: 20px !important;
        background: rgba(102, 126, 234, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .uploadedFile:hover {
        background: rgba(102, 126, 234, 0.10) !important;
        border-color: #764ba2 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #333 !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%) !important;
    }
    
    /* Input Box */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Chat Input */
    .stChatInput > div {
        border-radius: 16px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 4px !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Success/Warning/Error Messages */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid !important;
    }
    
    .stAlertSuccess {
        border-color: #28a745 !important;
    }
    
    .stAlertError {
        border-color: #dc3545 !important;
    }
    
    .stAlertWarning {
        border-color: #ffc107 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = DocumentAgent()
if "ingested_count" not in st.session_state:
    st.session_state.ingested_count = 0
if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0

# Sidebar
with st.sidebar:
    # Navigation
    st.markdown("### 🧭 Navigation")
    st.page_link("streamlit_app.py", label="Chat", icon="💬")
    st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/upload.py", label="Upload", icon="📤")
    st.page_link("pages/settings.py", label="Settings", icon="⚙️")
    
    st.divider()
    
    # Logo and title
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <span style="font-size: 2.5rem;">📄</span>
        <h2 style="margin: 0; color: #2E86AB;">DocIntel</h2>
        <p style="color: #666; margin: 0; font-size: 0.8rem;">Document Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Upload section
    st.subheader("📤 Quick Upload")
    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx", "txt"],
        key="sidebar_upload",
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        if st.button("🚀 Process", type="primary", width="stretch"):
            with st.spinner("🔄 Processing..."):
                try:
                    pipeline = IngestionPipeline()
                    result = pipeline.process_document(
                        tmp_path,
                        {
                            "uploaded_at": str(datetime.now()),
                            "filename": uploaded_file.name,
                            "user": "demo"
                        }
                    )
                    st.session_state.ingested_count += result["chunks"]
                    st.session_state.doc_count += 1
                    st.success(f"✅ {result['chunks']} chunks added!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    st.divider()
    
    # Analytics Dashboard
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "📄 Documents",
            st.session_state.doc_count,
            delta="+1" if st.session_state.doc_count > 0 else None
        )
    with col2:
        st.metric(
            "📝 Chunks",
            st.session_state.ingested_count,
            delta=f"+{st.session_state.ingested_count}" if st.session_state.ingested_count > 0 else None
        )
    
    # Confidence gauge
    if st.session_state.messages:
        last_msg = st.session_state.messages[-1]
        if "confidence" in last_msg:
            confidence = last_msg["confidence"] * 100
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=confidence,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Last Response Confidence"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"},
                        {'range': [80, 100], 'color': "darkgray"}
                    ]
                }
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    if st.button("🗑️ Clear Chat", width="stretch"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🧹 Reset Database", width="stretch"):
        from app.vector_store.chroma_client import ChromaClient
        ChromaClient().delete_all()
        st.session_state.ingested_count = 0
        st.session_state.doc_count = 0
        st.success("Database cleared!")
        st.rerun()
    
    st.divider()
    st.caption("⚡ Powered by Groq + LangGraph + ChromaDB")

# Main chat interface
st.markdown('<div class="main-header">🧠 Ask Your Documents</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Q&A, Summarization & Data Extraction</div>', unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Show sources for assistant messages
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            with st.expander("📚 View Sources", expanded=False):
                for idx, src in enumerate(msg["sources"][:3]):
                    st.markdown(f"**Source {idx+1}** (Score: {src.get('score', 0):.2f})")
                    st.markdown(f'<div class="source-box">{src["document"][:300]}...</div>', unsafe_allow_html=True)
        
        # Show confidence
        if "confidence" in msg:
            conf = msg["confidence"] * 100
            st.caption(f"🎯 Confidence: {conf:.0f}% {'✅ High' if conf > 70 else '⚠️ Medium' if conf > 40 else '❓ Low'}")

# Input
if prompt := st.chat_input("Ask about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Analyzing documents..."):
            try:
                # Process with agent
                result = st.session_state.agent.process_query(prompt)
                
                response = result.get("response", "I couldn't find an answer.")
                confidence = result.get("confidence", 0.0)
                sources = result.get("sources", [])
                intent = result.get("intent", "unknown")
                
                st.markdown(response)
                
                # Show sources
                if sources:
                    with st.expander("📚 View Sources", expanded=False):
                        for idx, src in enumerate(sources[:3]):
                            st.markdown(f"**Source {idx+1}** (Score: {src.get('score', 0):.2f})")
                            doc_text = src.get("document", "")[:300]
                            st.markdown(f'<div class="source-box">{doc_text}...</div>', unsafe_allow_html=True)
                
                # Show metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"🎯 Confidence: {confidence*100:.0f}%")
                with col2:
                    st.caption(f"📋 Intent: {intent}")
                with col3:
                    if sources:
                        st.caption(f"📚 Sources: {len(sources[:3])}")
                
                # Store in history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources[:3],
                    "confidence": confidence,
                    "intent": intent
                })
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {str(e)}",
                    "confidence": 0,
                    "sources": []
                })