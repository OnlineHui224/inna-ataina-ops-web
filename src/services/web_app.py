import os
import sys
from pathlib import Path
import tempfile

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.gemini_extractor import GeminiExtractor


def _get_gemini_api_key() -> str:
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]

    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""

# 1. Setup the Webpage Title and Header
st.set_page_config(page_title="INNA ATAINA OPS PRO", page_icon="✈️", layout="centered")

st.title("✈️ INNA ATAINA TRAVELS")
st.subheader("Operations Automation Pro")
st.markdown("**Developed by AIO Scholarworks**")
st.divider()

# 2. Create the File Drag-and-Drop Box
uploaded_file = st.file_uploader("Upload Travel Ticket (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

# 3. Create the Run Button
if st.button("Extract Ticket Data", type="primary"):
    if uploaded_file is not None:
        with st.spinner("AI is reading the ticket... Please wait."):
            
            # Save a quick temporary copy of the file so the AI can look at it
            file_extension = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                # Wake up your custom AI engine
                api_key = _get_gemini_api_key()
                if not api_key:
                    st.error("GEMINI_API_KEY is not configured in Streamlit secrets or environment variables.")
                    st.stop()

                extractor = GeminiExtractor(api_key)
                extracted_data = extractor.process_document(tmp_path)
                
                st.success("Extraction 100% Successful!")
                
                # Show the clean formatted aviation data right on the website
                st.json(extracted_data.model_dump()) 
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
            finally:
                # Clean up the temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    else:
        st.warning("Please upload a ticket first!")