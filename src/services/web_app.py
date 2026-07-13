import os
import sys
from pathlib import Path
import tempfile
import streamlit as st
import pandas as pd 

# --- PATH SETUP ---
CURRENT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = CURRENT_DIR.parent.parent.resolve()

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gemini_extractor import GeminiExtractor
from visa_extractor import VisaExtractor
from excel_logger import ExcelLogger

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

@st.cache_data
def load_hotel_database():
    excel_path = os.path.join(str(REPO_ROOT), "assets", "hotels.xlsx")
    default_makkah = ["Select a Makkah hotel..."]
    default_madinah = ["Select a Madinah hotel..."]
    
    if not os.path.exists(excel_path):
        return default_makkah + ["⚠️ Missing hotels.xlsx"], default_madinah + ["⚠️ Missing hotels.xlsx"]
        
    try:
        df = pd.read_excel(excel_path)
        cols = df.columns.astype(str).str.strip().str.lower()
        df.columns = cols
        hotel_col = next((c for c in cols if 'english' in c or 'hotel name' in c), cols[1] if len(cols) > 1 else cols[0])
        city_col = next((c for c in cols if 'city' in c), cols[3] if len(cols) > 3 else cols[-1])
        
        df[hotel_col] = df[hotel_col].astype(str).str.strip()
        df[city_col] = df[city_col].astype(str).str.strip().str.lower()
        
        makkah_mask = df[city_col].str.contains('makkah|mecca', na=False)
        makkah_list = sorted([h for h in df[makkah_mask][hotel_col].unique().tolist() if h.lower() != 'nan' and h != ''])
        
        madinah_mask = df[city_col].str.contains('madina|medina', na=False)
        madinah_list = sorted([h for h in df[madinah_mask][hotel_col].unique().tolist() if h.lower() != 'nan' and h != ''])
        
        return default_makkah + makkah_list, default_madinah + madinah_list
    except Exception as e:
        return default_makkah + [f"⚠️ Error: {e}"], default_madinah + [f"⚠️ Error: {e}"]

st.set_page_config(page_title="INNA ATAINA OPS PRO", page_icon="✈️", layout="wide") 

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

st.title("✈️ INNA ATAINA TRAVELS ✈️")
st.subheader("Operations Automation Pro (OPS PRO)")
st.divider()

# ==========================================
# THE TAB SYSTEM (MODULES SEPARATED)
# ==========================================
tab_flights, tab_visas = st.tabs(["🎫 Flight Document Generator", "🛂 Visa & Logistics Logger"])

# ------------------------------------------
# TAB 1: FLIGHTS (Your original setup)
# ------------------------------------------
with tab_flights:
    st.markdown("### Generate Word Itineraries")
    uploaded_files = st.file_uploader("Upload Travel Tickets (PDF, JPG, PNG)", type=["pdf", "jpg", "png"], accept_multiple_files=True, key="flight_up")

    if st.button("1. Extract Flight Data"):
        if uploaded_files and len(uploaded_files) > 0:
            with st.spinner("OPS PRO is reading file(s)..."):
                try:
                    api_key = _get_gemini_api_key()
                    if not api_key:
                        st.error("API Key missing.")
                        st.stop()
                    extractor = GeminiExtractor(api_key)
                    st.session_state.extracted_data = extractor.extract(uploaded_files)
                    st.success("Flight Extraction Successful!")
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")
        else:
            st.warning("Upload a ticket first.")

    if st.session_state.extracted_data is not None:
        makkah_options, madinah_options = load_hotel_database()
        col1, col2, col3 = st.columns(3)
        with col1:
            group_name_input = st.text_input("Group Name (Optional)", placeholder="Type group name...")
        with col2:
            makkah_hotel_input = st.selectbox("Makkah Hotel", options=makkah_options)
        with col3:
            madinah_hotel_input = st.selectbox("Madinah Hotel", options=madinah_options)

        if st.button("2. Generate Word Document", type="primary"):
            if DocxGenerator is None:
                st.error("Docx Generator missing.")
            else:
                with st.spinner("Generating..."):
                    try:
                        template_path = os.path.join(str(REPO_ROOT), "assets", "blank_template.docx")
                        output_dir = os.path.join(str(REPO_ROOT), "output")
                        generator = DocxGenerator(template_path=template_path, output_dir=output_dir)
                        
                        m_mak = "" if "Select a Makkah" in makkah_hotel_input else makkah_hotel_input
                        m_mad = "" if "Select a Madinah" in madinah_hotel_input else madinah_hotel_input
                        
                        doc_file_path = generator.generate(st.session_state.extracted_data, m_mak, m_mad, group_name_input)
                        
                        with open(doc_file_path, "rb") as file:
                            st.download_button("📥 Download Itinerary (Word Doc)", data=file, file_name=os.path.basename(doc_file_path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    except Exception as e:
                        st.error(f"Failed: {e}")

# ------------------------------------------
# TAB 2: VISAS & LOGISTICS (The New Excel Tool)
# ------------------------------------------
with tab_visas:
    st.markdown("### Master Excel Database Logger")
    st.info("Extract visa details and log the full package directly to the Master Excel File.")
    
    AGENT_LIST = ["Select Agent...", "Ginger Travelz", "Agent B", "Agent C"]
    TRANSPORT_LIST = ["Select Transport...", "Standard Bus", "VIP GMC", "Private Car", "Train"]
    VISA_COMPANY_LIST = ["Select Visa Company...", "Company A", "Company B", "Company C"]
    makkah_options, madinah_options = load_hotel_database()

    colA, colB = st.columns(2)
    with colA:
        sel_agent = st.selectbox("Agent Name", options=AGENT_LIST)
        sel_transport = st.selectbox("Transportation Package", options=TRANSPORT_LIST)
        sel_visa_comp = st.selectbox("Visa Insurance Company", options=VISA_COMPANY_LIST)
    with colB:
        sel_makkah = st.selectbox("Makkah Hotel (Visa Log)", options=makkah_options, key="v_mak")
        sel_madinah = st.selectbox("Madinah Hotel (Visa Log)", options=madinah_options, key="v_mad")
        
    col_dep, col_arr = st.columns(2)
    with col_dep:
        date_dep = st.date_input("Departure Date")
    with col_arr:
        date_arr = st.date_input("Arrival Date")

    st.divider()
    visa_file = st.file_uploader("Upload Visa Document (PDF/Image)", type=["pdf", "jpg", "png"], key="visa_up")
    
    if st.button("🚀 Extract Visa & Log to Excel", type="primary"):
        if visa_file is None:
            st.error("Upload a Visa document first!")
        elif "Select" in sel_agent or "Select" in sel_transport or "Select" in sel_visa_comp:
            st.warning("Please select Agent, Transport, and Visa Company from the dropdowns.")
        else:
            with st.spinner("Extracting Visa Data & Updating Excel..."):
                try:
                    api_key = _get_gemini_api_key()
                    v_extractor = VisaExtractor(api_key)
                    db_logger = ExcelLogger()
                    
                    visa_data = v_extractor.extract(visa_file)
                    
                    full_log_data = {
                        "AGENT NAME": sel_agent,
                        "VISA NUMBER": visa_data.get("VISA NUMBER", "N/A"),
                        "PASSPORT NUMBER": visa_data.get("PASSPORT NUMBER", "N/A"),
                        "NAME": visa_data.get("NAME", "N/A"),
                        "DEPARTURE DATE": date_dep.strftime("%d-%b-%Y"),
                        "ARRIVAL DATE": date_arr.strftime("%d-%b-%Y"),
                        "MAKKAH HOTEL": sel_makkah,
                        "MEDINAH HOTEL": sel_madinah,
                        "TRANSPORTATION": sel_transport,
                        "VISA COMPANY": sel_visa_comp
                    }
                    
                    file_path = db_logger.log_visa(full_log_data)
                    st.success(f"✅ Successfully logged **{visa_data.get('NAME')}** to Excel!")
                    
                    with open(file_path, "rb") as f:
                        st.download_button("📥 Download Updated Excel Database", data=f, file_name="contract_visas_documentation.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception as e:
                    st.error(f"Failed to log data: {e}")
