import sys
import os
# This line tells Python exactly where your project folders are so it doesn't get lost
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import tempfile
from src.services.gemini_extractor import GeminiExtractor

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
                extractor = GeminiExtractor()
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