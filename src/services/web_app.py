import os
import sys
from pathlib import Path
import tempfile
import streamlit as st

# --- THE COMPLETE PATH FIX ---
CURRENT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = CURRENT_DIR.parent.parent.resolve()

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gemini_extractor import GeminiExtractor

# --- IMPORTING YOUR EXACT DOCX GENERATOR ---
try:
    from docx_generator import DocxGenerator
    DOCX_ERROR = None
except Exception as e:
    DocxGenerator = None
    DOCX_ERROR = str(e)

# --- API KEY FUNCTION ---
def _get_gemini_api_key() -> str:
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    return (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()


# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="INNA ATAINA OPS PRO", page_icon="✈️", layout="centered")

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None


# --- 2. SIDEBAR DESIGN ---
st.sidebar.title("✈️ INNA ATAINA TRAVELS")
st.sidebar.markdown("### OPS PRO")
st.sidebar.divider()
st.sidebar.info("Step 1: Upload and extract the ticket data on the main screen.\n\nStep 2: Generate the document here.")


# --- 3. MAIN PAGE UI ---
st.title("✈️ INNA ATAINA TRAVELS")
st.subheader("Operations Automation Pro")
st.markdown("**Developed by AIO Scholarworks**")
st.divider()

uploaded_file = st.file_uploader("Upload Travel Ticket (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

# --- BUTTON 1: EXTRACT DATA ---
if st.button("1. Extract Ticket Data", type="primary"):
    if uploaded_file is not None:
        with st.spinner("AI is reading the ticket... Please wait."):
            
            file_extension = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                api_key = _get_gemini_api_key()
                if not api_key:
                    st.error("GEMINI_API_KEY is not configured.")
                    st.stop()

                extractor = GeminiExtractor(api_key)
                extracted_data = extractor.process_document(tmp_path)
                
                if extracted_data is None:
                    st.error("Extraction failed. The AI returned an empty response.")
                    st.code(getattr(extractor, "last_error", "Unknown Error"))
                else:
                    st.success("Extraction 100% Successful!")
                    st.session_state.extracted_data = extracted_data
                    st.json(extracted_data.model_dump()) 
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    else:
        st.warning("Please upload a ticket first!")


# --- BUTTON 2: GENERATE DOCUMENT ---
if st.session_state.extracted_data is not None:
    st.divider()
    st.success("✅ Ticket data saved in memory! Ready to generate document.")
    
    with st.sidebar:
        if st.button("2. Generate Document", type="primary"):
            if DocxGenerator is None:
                st.error(f"Cannot load your document file! Error: {DOCX_ERROR}")
            else:
                with st.spinner("Generating Word Document..."):
                    try:
                        # Setup the exact folder paths your code expects
                        template_path = os.path.join(str(REPO_ROOT), "assets", "template.docx")
                        output_dir = os.path.join(str(REPO_ROOT), "output")
                        
                        # Use your exact class name and required variables
                        generator = DocxGenerator(template_path=template_path, output_dir=output_dir)
                        
                        # Use your exact function name (.generate instead of .create_document)
                        doc_file_path = generator.generate(st.session_state.extracted_data)
                        
                        # Grab the safe file name your code created
                        final_file_name = os.path.basename(doc_file_path)
                        
                        with open(doc_file_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Itinerary (Word Doc)",
                                data=file,
                                file_name=final_file_name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    except Exception as e:
                        st.error(f"Document generation failed: {e}")
