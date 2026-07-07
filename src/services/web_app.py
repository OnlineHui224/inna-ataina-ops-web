import os
import sys
from pathlib import Path
import tempfile
import streamlit as st

# --- THE COMPLETE PATH FIX ---
# 1. Find our exact locations on the cloud server
CURRENT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = CURRENT_DIR.parent.parent.resolve()

# 2. Tell Python to look in the current folder (so web_app can find gemini_extractor)
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# 3. Tell Python to look at the master root folder (so gemini_extractor can find src.core and src.models)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Now all imports will work flawlessly!
from gemini_extractor import GeminiExtractor


# --- COPILOT'S IMPROVED API KEY FUNCTION ---
def _get_gemini_api_key() -> str:
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    return (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()


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

            # --- COPILOT'S IMPROVED TRY BLOCK ---
            try:
                api_key = _get_gemini_api_key()
                if not api_key:
                    st.error("GEMINI_API_KEY is not configured in Streamlit secrets or environment variables.")
                    st.stop()

                extractor = GeminiExtractor(api_key)
                extracted_data = extractor.process_document(tmp_path)
                
                if extracted_data is None:
                    st.error("Extraction failed. The AI returned an empty response.")
                    # Copilot's trick to show the exact error from the engine:
                    st.code(getattr(extractor, "last_error", "Check ticket formatting or API key quota."))
                else:
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
