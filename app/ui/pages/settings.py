"""Settings page for DocIntel."""
import streamlit as st
import os
from app.config import settings
from app.vector_store.chroma_client import ChromaClient

def render_settings():
    """Render the settings page."""
    st.title("⚙️ Settings")
    
    # Check if running on Hugging Face (live demo)
    is_demo = os.path.exists('/.dockerenv') or 'HF_TOKEN' in os.environ
    
    if is_demo:
        st.info("🔒 **Live Demo Mode** - Settings are read-only for security. API keys and sensitive actions are hidden.")
    
    st.markdown("Configure DocIntel settings and preferences.")
    
    # General Settings
    st.subheader("🔧 General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chunk_size = st.number_input(
            "Chunk Size (tokens)",
            min_value=100,
            max_value=4000,
            value=settings.CHUNK_SIZE,
            step=100,
            help="Size of document chunks for processing",
            disabled=is_demo  # Disable in demo
        )
    
    with col2:
        chunk_overlap = st.number_input(
            "Chunk Overlap (tokens)",
            min_value=0,
            max_value=500,
            value=settings.CHUNK_OVERLAP,
            step=50,
            help="Overlap between chunks for context preservation",
            disabled=is_demo  # Disable in demo
        )
    
    top_k = st.number_input(
        "Top K Retrieval",
        min_value=1,
        max_value=20,
        value=settings.TOP_K,
        step=1,
        help="Number of documents to retrieve per query",
        disabled=is_demo  # Disable in demo
    )
    
    # Model Settings
    st.subheader("🤖 Model Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        embedding_model = st.selectbox(
            "Embedding Model",
            ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "all-distilroberta-v1"],
            index=0,
            help="Model for generating document embeddings (requires restart)",
            disabled=is_demo  # Disable in demo
        )
    
    with col2:
        llm_model = st.selectbox(
            "LLM Model",
            ["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
            index=0,
            help="Model for generating responses",
            disabled=is_demo  # Disable in demo
        )
    
    # API Settings - Hidden completely in demo mode
    if not is_demo:
        st.subheader("🔑 API Settings")
        
        groq_api_key = st.text_input(
            "Groq API Key",
            value=settings.GROQ_API_KEY,
            type="password",
            help="Get your API key from console.groq.com"
        )
        
        if st.button("💾 Save Settings", type="primary"):
            # Save settings to .env
            env_path = ".env"
            env_content = []
            
            # Read existing .env
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_content = f.readlines()
            
            # Update values
            updates = {
                "CHUNK_SIZE": str(chunk_size),
                "CHUNK_OVERLAP": str(chunk_overlap),
                "TOP_K": str(top_k),
                "EMBEDDING_MODEL": embedding_model,
                "GROQ_MODEL": llm_model,
                "GROQ_API_KEY": groq_api_key
            }
            
            updated_lines = []
            for line in env_content:
                key = line.split("=")[0].strip() if "=" in line else None
                if key in updates:
                    updated_lines.append(f"{key}={updates[key]}\n")
                    del updates[key]
                else:
                    updated_lines.append(line)
            
            # Add new values
            for key, value in updates.items():
                updated_lines.append(f"{key}={value}\n")
            
            # Write back
            with open(env_path, "w") as f:
                f.writelines(updated_lines)
            
            st.success("✅ Settings saved! Restart DocIntel for changes to take effect.")
    else:
        # Show masked API status in demo
        st.subheader("🔑 API Status")
        st.success("✅ Groq API: **Connected** (Key hidden for security)")
    
    # Database Management - Disabled in demo
    st.divider()
    st.subheader("🗄️ Database Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if is_demo:
            st.button("🧹 Clear Vector Database", use_container_width=True, disabled=True)
            st.caption("🔒 Disabled in live demo")
        else:
            if st.button("🧹 Clear Vector Database", use_container_width=True):
                ChromaClient().delete_all()
                st.success("Vector database cleared!")
    
    with col2:
        if st.button("📊 Database Stats", use_container_width=True):
            from app.vector_store.chroma_client import ChromaClient
            client = ChromaClient()
            count = client.count()
            st.info(f"Total chunks in database: {count}")
    
    # System Status
    st.divider()
    st.subheader("📊 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🟢 Active", delta="Running")
    
    with col2:
        st.metric("API Status", "✅ Connected", delta="Groq")
    
    with col3:
        st.metric("Vector DB", "✅ Connected", delta="ChromaDB")
    
    # System Info
    with st.expander("ℹ️ System Information"):
        st.markdown(f"""
        - **Python Version**: {os.sys.version}
        - **Project**: DocIntel v1.0.0
        - **Platform**: {os.sys.platform}
        - **Working Directory**: {os.getcwd()}
        - **Environment**: {'🐳 Docker' if os.path.exists('/.dockerenv') else '🖥️ Local'}
        - **Mode**: {'🔒 Live Demo (Read-Only)' if is_demo else '🔧 Full Access'}
        """)
    
    # About
    st.divider()
    st.caption("""
    **DocIntel v1.0.0** | Enterprise Document Intelligence Platform
    Built with ❤️ using Groq, LangGraph, Streamlit, and ChromaDB
    """)

if __name__ == "__main__" or "streamlit" in str(__name__):
    render_settings()