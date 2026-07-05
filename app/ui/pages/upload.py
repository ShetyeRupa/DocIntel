"""Document upload page for DocIntel."""
import streamlit as st
from app.ingestion.pipeline import IngestionPipeline
import tempfile
import os
from datetime import datetime

def render_upload():
    """Render the document upload page."""
    st.title("📤 Upload Documents")
    st.markdown("Upload documents to index and make them searchable.")
    
    # File upload section
    st.subheader("📁 Upload Files")
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_files:
        st.info(f"Selected {len(uploaded_files)} file(s) for upload.")
        
        # Document metadata
        st.subheader("📋 Document Metadata (Optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox(
                "Department",
                ["General", "Legal", "Finance", "Operations", "HR", "Research"]
            )
        with col2:
            category = st.selectbox(
                "Category",
                ["General", "Contract", "Invoice", "Report", "Policy", "Research Paper"]
            )
        
        tags = st.text_input("Tags (comma-separated)", placeholder="e.g., contract, legal, important")
        
        if st.button("🚀 Process Documents", type="primary", use_container_width=True):
            pipeline = IngestionPipeline()
            successful = []
            failed = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing: {file.name}")
                
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=f".{file.name.split('.')[-1]}"
                    ) as tmp:
                        tmp.write(file.getvalue())
                        tmp_path = tmp.name
                    
                    # Process document
                    result = pipeline.process_document(
                        tmp_path,
                        {
                            "department": department,
                            "category": category,
                            "tags": tags.split(",") if tags else [],
                            "uploaded_at": str(datetime.now()),
                            "filename": file.name
                        }
                    )
                    
                    successful.append({
                        "filename": file.name,
                        "chunks": result.get("chunks", 0)
                    })
                    
                    # Cleanup
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    failed.append({
                        "filename": file.name,
                        "error": str(e)
                    })
                
                # Update progress
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("Processing complete!")
            
            # Show results
            st.divider()
            st.subheader("📊 Processing Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("✅ Successful", len(successful))
            with col2:
                st.metric("❌ Failed", len(failed))
            
            if successful:
                st.success(f"Successfully processed {len(successful)} documents!")
                for doc in successful:
                    st.markdown(f"- **{doc['filename']}**: {doc['chunks']} chunks created")
            
            if failed:
                st.error(f"Failed to process {len(failed)} documents:")
                for doc in failed:
                    st.markdown(f"- **{doc['filename']}**: {doc['error']}")
    
    # Document management
    st.divider()
    st.subheader("📚 Document Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Documents", use_container_width=True):
            from app.vector_store.chroma_client import ChromaClient
            ChromaClient().delete_all()
            st.success("All documents cleared!")
            st.rerun()
    
    with col2:
        if st.button("📊 View Document Stats", use_container_width=True):
            from app.vector_store.chroma_client import ChromaClient
            count = ChromaClient().count()
            st.info(f"Total documents in database: {count}")
    
    # Upload tips
    with st.expander("💡 Upload Tips"):
        st.markdown("""
        **Best Practices:**
        - Upload PDFs with selectable text (scanned images may not work well)
        - For large documents (>100 pages), consider splitting into sections
        - Add descriptive metadata to help with search
        - Use tags to organize documents by topic or project
        
        **Supported Formats:**
        - **PDF**: Best for contracts, reports, and research papers
        - **DOCX**: Best for editable documents and proposals
        - **TXT**: Best for plain text files and notes
        
        **Limitations:**
        - Maximum file size: 50MB
        - Maximum pages: 1000
        - Processing time: ~1 sec per page
        """)

if __name__ == "__main__" or "streamlit" in str(__name__):
    render_upload()