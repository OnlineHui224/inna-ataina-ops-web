import os
import sys
from pathlib import Path
import tempfile
import streamlit as st
import pandas as pd 

# --- THE COMPLETE PATH FIX ---
CURRENT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = CURRENT_DIR.parent.parent.resolve()

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gemini_extractor import GeminiExtractor

try:
    from docx_generator import DocxGenerator
    DOCX_ERROR = None
except Exception as e:
    DocxGenerator = None
    DOCX_ERROR = str(e)

def _get_gemini_api_key() -> str:
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    return (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()


# --- SMART EXCEL FILTER (MATCHES YOUR SCREENSHOT EXACTLY) ---
@st.cache_data
def load_hotel_database():
    excel_path = os.path.join(str(REPO_ROOT), "assets", "hotels.xlsx")
    
    default_makkah = ["Select a Makkah hotel..."]
    default_madinah = ["Select a Madinah hotel..."]
    
    if not os.path.exists(excel_path):
        return default_makkah + ["⚠️ Missing assets/hotels.xlsx file"], default_madinah + ["⚠️ Missing assets/hotels.xlsx file"]
        
    try:
        # Read the Excel sheet
        df = pd.read_excel(excel_path)
        
        if df.empty:
            return default_makkah + ["⚠️ Excel sheet is empty"], default_madinah + ["⚠️ Excel sheet is empty"]
            
        # Standardize column names so it doesn't crash if there's an extra space
        cols = df.columns.astype(str).str.strip().str.lower()
        df.columns = cols
        
        # Dynamically find the "English Name" column and the "City" column
        hotel_col = next((c for c in cols if 'english' in c or 'hotel name' in c), cols[1] if len(cols) > 1 else cols[0])
        city_col = next((c for c in cols if 'city' in c), cols[3] if len(cols) > 3 else cols[-1])
        
        # Clean the data
        df[hotel_col] = df[hotel_col].astype(str).str.strip()
        df[city_col] = df[city_col].astype(str).str.strip().str.lower()
        
        # 1. Grab all Makkah Hotels
        makkah_mask = df[city_col].str.contains('makkah|mecca', na=False)
        makkah_list = df[makkah_mask][hotel_col].unique().tolist()
        makkah_list = [h for h in makkah_list if h.lower() != 'nan' and h != '']
        makkah_list.sort()
        
        # 2. Grab all Madinah Hotels (handles "Madina" like in your screenshot)
        madinah_mask = df[city_col].str.contains('madina|medina', na=False)
        madinah_list = df[madinah_mask][hotel_col].unique().tolist()
        madinah_list = [h for h in madinah_list if h.lower() != 'nan' and h != '']
        madinah_list.sort()
        
        return default_makkah + makkah_list, default_madinah + madinah_list
        
    except Exception as e:
        error_msg = f"⚠️ Excel Error: {str(e)}"
        return default_makkah + [error_msg], default_madinah + [error_msg]


# --- 1. PAGE SETUP & MEMORY ---
st.set_page_config(page_title="INNA ATAINA OPS PRO", page_icon="✈️", layout="wide") 

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None


# --- 2. SIDEBAR DESIGN ---
st.sidebar.title("✈️ INNA ATAINA TRAVELS ✈️")
st.sidebar.markdown("### OPS PRO")
st.sidebar.divider()
st.sidebar.info("Step 1: Upload and extract the ticket data on the main screen.\n\nStep 2: Generate the document here.")


# --- 3. MAIN PAGE UI ---
st.title("✈️ INNA ATAINA TRAVELS ✈️")
st.subheader("Operations Automation Pro (OPS PRO)")
st.markdown("**Developed by AIO Scholarworks**")
st.divider()

# --- UPGRADED MULTI-FILE UPLOADER ---
# Notice we added accept_multiple_files=True
uploaded_files = st.file_uploader(
    "Upload Travel Tickets (PDF, JPG, PNG)", 
    type=["pdf", "jpg", "png"], 
    accept_multiple_files=True 
)

if st.button("1. Extract Ticket Data"):
    # Check if the list has at least one file in it
    if uploaded_files and len(uploaded_files) > 0:
        with st.spinner(f" OPS PRO is reading {len(uploaded_files)} file(s)... Please wait."):
            try:
                # Pass the ENTIRE list of files to the extractor at once
                st.session_state.ticket_data = extractor.extract(uploaded_files)
                st.success("Extraction successful! Review the data below.")
            except Exception as e:
                st.error(f"Extraction failed: {str(e)}")
    else:
        st.warning("Please upload at least one ticket before extracting.")
            
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
                else:
                    st.success("Extraction 100% Successful!")
                    st.session_state.extracted_data = extracted_data
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    else:
        st.warning("Please upload a ticket first!")


if st.session_state.extracted_data is not None:
    st.divider()
    st.subheader("📝 Step 2: Finalize Document Details")
    
    # Run the smart filter!
    makkah_options, madinah_options = load_hotel_database()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("👥 Client Info")
        group_name_input = st.text_input("Group Name (Optional)", placeholder="Type group name here...")
        
    with col2:
        st.warning("🕋 Makkah Accommodation")
        makkah_hotel_input = st.selectbox("Select Makkah Hotel", options=makkah_options)
        
    with col3:
        st.success("🕌 Madinah Accommodation")
        madinah_hotel_input = st.selectbox("Select Madinah Hotel", options=madinah_options)

    with st.expander("🔍 View Raw Flight Data"):
        st.json(st.session_state.extracted_data.model_dump()) 

    with st.sidebar:
        if st.button("2. Generate Document", type="primary"):
            if DocxGenerator is None:
                st.error(f"Cannot load your document file! Error: {DOCX_ERROR}")
            else:
                with st.spinner("Generating Word Document..."):
                    try:
                        template_path = os.path.join(str(REPO_ROOT), "assets", "blank_template.docx")
                        output_dir = os.path.join(str(REPO_ROOT), "output")
                        
                        generator = DocxGenerator(template_path=template_path, output_dir=output_dir)
                        
                        makkah_val = "" if "Select a Makkah" in makkah_hotel_input or "⚠️" in makkah_hotel_input else makkah_hotel_input
                        madinah_val = "" if "Select a Madinah" in madinah_hotel_input or "⚠️" in madinah_hotel_input else madinah_hotel_input
                        
                        doc_file_path = generator.generate(
                            data=st.session_state.extracted_data,
                            makkah_hotel=makkah_val,
                            madinah_hotel=madinah_val,
                            group_name=group_name_input
                        )
                        
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
