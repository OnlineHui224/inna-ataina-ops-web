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

# Import your custom tools
from gemini_extractor import GeminiExtractor

# Try to import your document generator (adjust the names if your file uses different ones)
try:
    from docx_generator import DocumentGenerator
except ImportError:
    DocumentGenerator = None


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

# Create a "Memory" to hold the ticket data after it is extracted
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
                    
                    # 🚨 SAVE TO MEMORY SO THE DOCX GENERATOR CAN USE IT
                    st.session_state.extracted_data = extracted_data
                    
                    st.json(extracted_data.model_dump()) 
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    else:
        st.warning("Please upload a ticket first!")


# --- BUTTON 2: GENERATE DOCUMENT (Only shows if data exists in memory) ---
if st.session_state.extracted_data is not None:
    st.divider()
    st.success("✅ Ticket data saved in memory! Ready to generate document.")
    
    # We put the document button in the sidebar to match your screenshot
    with st.sidebar:
        if st.button("2. Generate Document", type="primary"):
            if DocumentGenerator is None:
                st.error("Could not load `docx_generator.py`. Please check your file imports!")
            else:
                with st.spinner("Generating Word Document..."):
                    try:
                        # Wake up your document generator and pass it the memory data
                        generator = DocumentGenerator()
                        doc_file_path = generator.create_document(st.session_state.extracted_data)
                        
                        # Provide the final download button
                        with open(doc_file_path, "rb") as file:
                            st.download_button(
                                label="📥 Download Itinerary (Word Doc)",
                                data=file,
                                file_name="Inna_Ataina_Itinerary.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    except Exception as e:
                        st.error(f"Document generation failed: {e}")
