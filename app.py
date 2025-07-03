import streamlit as st
import json
import os
from file_reader import extract_text
from metadata_extractor import extract_metadata

# Page configuration
st.set_page_config(
    page_title="Metadata Extractor",
    page_icon="logom.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    
    .metadata-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1> Metadata Extractor</h1>
    <p>Transform your documents into structured metadata using advanced AI technology</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with information and settings
with st.sidebar:
   st.markdown("""
   <div style='
    background: linear-gradient(to right, #667eea, #764ba2);
    padding: 1.5rem;
    border-radius: 12px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
   '>
    <h4 style='margin-top: 0;'>📋 How it Works</h4>
    <p style='margin: 0.5rem 0;'> Step 1: Upload your document</p>
    <p style='margin: 0.5rem 0;'> Step 2: AI extracts text content</p>
    <p style='margin: 0.5rem 0;'> Step 3: Generate structured metadata</p>
    <p style='margin: 0.5rem 0;'> Step 4: Download results</p>
   </div>
   """, unsafe_allow_html=True)

    
with st.sidebar:
    st.markdown("""
    <div style='
        background: linear-gradient(to right, #667eea, #764ba2);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    '>
        <h4 style='margin-top: 0;'>📊 Supported Formats</h4>
        <p style='margin: 0.6rem 0;'>📄 <b>PDF</b> – Portable Document Format</p>
        <p style='margin: 0.6rem 0;'>📝 <b>DOCX</b> – Microsoft Word Document</p>
        <p style='margin: 0.6rem 0;'>📋 <b>TXT</b> – Plain Text File</p>
        <p style='margin: 0.6rem 0;'>🖼️ <b>PNG/JPG</b> – Image with OCR processing</p>
    </div>
    """, unsafe_allow_html=True)



    
    st.header("⚙️ Settings")
    max_file_size = st.slider("Max file size (MB)", 1, 200, 100)
    show_text_preview = st.checkbox("Show extracted text preview", value=True)

#
st.subheader("📤 Upload Your Document")
uploaded_file = st.file_uploader(
        label= "",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="Select a document to extract metadata from"
    )

# Processing section
if uploaded_file is not None:
    # File info display
    file_size_mb = uploaded_file.size / (1024 * 1024)
    file_type = uploaded_file.type or "Unknown"

    file_temp = """
    <div style='padding: 10px 15px; background-color: #1e1e2f; border-radius: 8px;'>
      <p style='margin: 0; color: #aaa;'>{icon} {label}</p>
      <p style='margin: 0; font-size: 18px; font-weight: bold; color: white;'>{value}</p>
    </div>
    """
    col1, col2, col3 = st.columns(3)

    with col1:
       st.markdown(file_temp.format(icon="📁", label="File Name", value=uploaded_file.name), unsafe_allow_html=True)

    with col2:
      st.markdown(file_temp.format(icon="📏", label="File Size", value=f"{file_size_mb:.2f} MB"), unsafe_allow_html=True)

    with col3:
       st.markdown(file_temp.format(icon="📋", label="File Type", value=file_type.split('/')[-1].upper()), unsafe_allow_html=True)

    
    # File size warning
    if file_size_mb > max_file_size:
        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ Large File Warning</strong><br>
            File size ({file_size_mb:.2f} MB) exceeds recommended limit ({max_file_size} MB). 
            Processing may take longer.
        </div>
        """, unsafe_allow_html=True)
     
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    # Process button
    if st.button("🚀 Start Processing", type="primary", use_container_width=True):
        try:
            # Save uploaded file
            file_path = os.path.join("temp_" + uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Success message
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ File Uploaded Successfully</strong><br>
                Ready to process: {uploaded_file.name}
            </div>
            """, unsafe_allow_html=True)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Extract text
            status_text.text("Extracting text from document...")
            progress_bar.progress(25)
            
            text = extract_text(file_path)
            
            progress_bar.progress(50)
            status_text.text("Text extraction completed!")
            
            # Show text preview if enabled
            if show_text_preview and text:
                with st.expander("Preview Extracted Text", expanded=False):
                    preview_text = text[:1000] + "..." if len(text) > 1000 else text
                    st.text_area("Extracted Content", preview_text, height=200, disabled=True)
                    st.caption(f"Showing first 1000 characters of {len(text)} total characters")
            
            # Generate metadata
            status_text.text("Generating metadata...")
            progress_bar.progress(75)
            
            metadata = extract_metadata(text,file_path)

            
            progress_bar.progress(100)
            status_text.text("✅ Processing completed!")
            
            # Display results
            st.markdown("""
            <div class="metadata-section">
                <h3>📊 Generated Metadata</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Metadata display in tabs
            tab1, tab2, tab3 = st.tabs(["📋 Formatted View", "🔧 JSON View", "📈 Analytics"])
            
            with tab1:
              file_info_card = """
               <div style='padding: 10px 15px; background-color: #1e1e2f; border-radius: 8px; margin-bottom: 1rem;'>
                <p style='margin: 0; color: #aaa;'>📌 {label}</p>
                <p style='margin: 0; font-size: 18px; font-weight: bold; color: white;'>{value}</p>
               </div>
               """
    
              if isinstance(metadata, dict):
                for key, value in metadata.items():
                  if isinstance(value, list):
                    st.markdown(f"<h4 style='color: white;'>📌 {key.title()}</h4>", unsafe_allow_html=True)

        # Card pill style for list items
                    card_style = """
                    <div style='
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        margin-bottom: 1rem;
                     '>
                        {items}
                    </div>
                     """

                    item_template = """
                    <div style='
                     background-color: #1e1e2f;
                     color: white;
                     padding: 8px 14px;
                     border-radius: 20px;
                     font-size: 14px;
                     box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                     '>{}</div>
                     """

                    items_html = ''.join([item_template.format(str(i)) for i in value])
                    st.markdown(card_style.format(items=items_html), unsafe_allow_html=True)

                  elif isinstance(value, dict):
                   st.markdown(f"<h4 style='color: white;'>📌 {key.title()}</h4>", unsafe_allow_html=True)
                   st.json(value)

                  else:
                     st.markdown(file_info_card.format(label=key.title(), value=value), unsafe_allow_html=True)

              else:
                    st.json(metadata)
            
            with tab2:
                st.json(metadata)
            
            with tab3:
                # Basic analytics
                if isinstance(metadata, dict):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(file_temp.format(icon="🔢",label=" Metadata Fields", value=len(metadata)),unsafe_allow_html=True)
                    with col2:
                        st.markdown(file_temp.format(icon="📝",label= "Text Length", value=len(text)),unsafe_allow_html=True)
                    with col3:
                        word_count = len(text.split()) if text else 0
                        st.markdown(file_temp.format(icon="📖",label= "Word Count", value=word_count),unsafe_allow_html=True)
            
            # Download section
            st.markdown("📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON download
                json_data = json.dumps(metadata, indent=2, ensure_ascii=False)
                st.download_button(
                    "Download Metadata (JSON)",
                    data=json_data,
                    file_name=f"{uploaded_file.name}_metadata.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # Text download
                if text:
                    st.download_button(
                        "Download Extracted Text",
                        data=text,
                        file_name=f"{uploaded_file.name}_extracted_text.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            # Clean up
            try:
                os.remove(file_path)
            except:
                pass
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            # Clean up on error
            try:
                if 'file_path' in locals():
                    os.remove(file_path)
            except:
                pass
