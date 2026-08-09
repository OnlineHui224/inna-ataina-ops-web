import os
import sys
from pathlib import Path
import tempfile
import streamlit as st
import pandas as pd

# --- PATH SETUP (unchanged) ---
CURRENT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = CURRENT_DIR.parent.parent.resolve()

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gemini_extractor import GeminiExtractor
from visa_extractor import VisaExtractor
from excel_logger import ExcelLogger
import ui_theme as T

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

# --- PRESENTATION LAYER ---
T.inject_theme(st)
T.hero(st, T.logo_data_uri(os.path.join(str(REPO_ROOT), "assets", "logo.png")))

# ==========================================
# THE TAB SYSTEM (MODULES SEPARATED)
# ==========================================
tab_flights, tab_visas = st.tabs(["🎫 FLIGHT DOCUMENT OPS PRO", "🛂 VISA & CONTRACT LOGGER OP"])

# ------------------------------------------
# TAB 1: FLIGHTS
# ------------------------------------------
with tab_flights:
    T.section(st, "", "Generate Word Itineraries")
    uploaded_files = st.file_uploader("Upload Travel Tickets (PDF, JPG, PNG)", type=["pdf", "jpg", "png"], accept_multiple_files=True, key="flight_up")
    if uploaded_files:
        T.file_chips(st, uploaded_files)

    if st.button("1. Extract Flight Data"):
        if uploaded_files and len(uploaded_files) > 0:
            with st.spinner("OPS PRO is reading file(s)..."):
                try:
                    api_key = _get_gemini_api_key()
                    if not api_key:
                        T.note(st, "bad", "<b>API Key missing.</b>")
                        st.stop()
                    extractor = GeminiExtractor(api_key)
                    st.session_state.extracted_data = extractor.extract(uploaded_files)
                    T.note(st, "ok", "<b>Flight Extraction Successful!</b>")
                except Exception as e:
                    T.note(st, "bad", f"<b>Extraction failed:</b> {str(e)}")
        else:
            T.note(st, "warn", "<b>Upload a ticket first.</b>")

    if st.session_state.extracted_data is not None:
        data = st.session_state.extracted_data

        T.section(st, "", "Extracted Journey")
        T.facts(st, [
            ("PASSENGER", data.passenger_name),
            ("PNR", data.pnr),
            ("CARRIER", data.primary_carrier),
            ("ADULTS", data.adults),
            ("CHILDREN", data.children),
            ("TOTAL PAX", data.total_pax),
        ])
        for f in data.flights:
            T.flight_leg(st, f.departure_city, f.arrival_city, f.departure_time,
                         f.arrival_time, f.date, f.carrier, f.flight_number)
        with st.expander("Raw extracted data"):
            st.json(data.model_dump() if hasattr(data, "model_dump") else data.dict())

        st.markdown("<hr>", unsafe_allow_html=True)
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
                T.note(st, "bad", "<b>Docx Generator missing.</b>")
            else:
                with st.spinner("Generating..."):
                    try:
                        template_path = os.path.join(str(REPO_ROOT), "assets", "blank_template.docx")
                        output_dir = os.path.join(str(REPO_ROOT), "output")
                        generator = DocxGenerator(template_path=template_path, output_dir=output_dir)

                        m_mak = "" if "Select a Makkah" in makkah_hotel_input else makkah_hotel_input
                        m_mad = "" if "Select a Madinah" in madinah_hotel_input else madinah_hotel_input

                        doc_file_path = generator.generate(st.session_state.extracted_data, m_mak, m_mad, group_name_input)

                        T.note(st, "ok", f"<b>Itinerary ready — {os.path.basename(doc_file_path)}</b>")
                        with open(doc_file_path, "rb") as file:
                            st.download_button("📥 Download Itinerary (Word Doc)", data=file, file_name=os.path.basename(doc_file_path), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    except Exception as e:
                        T.note(st, "bad", f"<b>Failed:</b> {e}")

# ------------------------------------------
# TAB 2: VISAS & LOGISTICS
# ------------------------------------------
with tab_visas:
    # Cloud URL Input (Hardcoded permanently)
    T.section(st, "", "Cloud Configuration")
    T.status_badge(st, "MASTER DATABASE", "Securely connected to Master Live Google Sheet")
    gsheet_url = "https://docs.google.com/spreadsheets/d/1_w-171YwDfTMP5OEwZv8khCOB_pUgvjKtZtgTFOzPeI/edit"
    st.markdown("<hr>", unsafe_allow_html=True)

    AGENT_LIST = [
        "Select Agent...", "Inna-Ataina", "AshTag", "Al-Mubarak", "Seriki Group",
        "Soaif Travel", "Mukareem", "AL-Lagusyy", "Al-Wafah", "Travel nest",
        "AT-Tibyan", "AL-Haqq", "AL-Bushrah", "AL-Shambagy", "Portfolio (Musty)",
        "AL-furqan", "Baseeroh", "Alh-Adua agba", "Nurul-qulub", "Nokbah",
        "Al-Jannah Travels", "Voyagemistry", "Umrah UK", "Saheed", "WakaNow", "Chiroma", "Other (Manual Entry)"
    ]
    TRANSPORT_LIST = [
        "Select Transport...", "Full Airport Transportation", "Half Airport Transportation",
        "Full Route Transportation", "Other (Manual Entry)"
    ]
    VISA_COMPANY_LIST = [
        "Select Visa Company...", "Aydh", "Roya", "Makareem", "LYN Contract", "Emaar", "Al-Mashaar",
        "Lamar", "Chiroma", "Ahali", "Other (Manual Entry)"
    ]

    makkah_options, madinah_options = load_hotel_database()
    makkah_options = list(makkah_options) + ["Other (Manual Entry)"]
    madinah_options = list(madinah_options) + ["Other (Manual Entry)"]

    colA, colB = st.columns(2)
    with colA:
      with st.container(border=True):
        T.group_label(st, "Agent & Package")
        sel_agent = st.selectbox("Agent Name", options=AGENT_LIST)
        final_agent = st.text_input("Type Agent Name:") if sel_agent == "Other (Manual Entry)" else sel_agent

        sel_transport = st.selectbox("Transportation Package", options=TRANSPORT_LIST)
        final_transport = st.text_input("Type Transportation:") if sel_transport == "Other (Manual Entry)" else sel_transport

        sel_visa_comp = st.selectbox("Visa Insurance Company", options=VISA_COMPANY_LIST)
        final_visa_comp = st.text_input("Type Visa Company:") if sel_visa_comp == "Other (Manual Entry)" else sel_visa_comp

    with colB:
      with st.container(border=True):
        T.group_label(st, "Accommodation")
        sel_makkah = st.selectbox("Makkah Hotel (Visa Log)", options=makkah_options, key="v_mak")
        final_makkah = st.text_input("Type Makkah Hotel:") if sel_makkah == "Other (Manual Entry)" else sel_makkah

        # Approved one-word fix: this compared against "Other (Manual Sheet)", so it never fired.
        sel_madinah = st.selectbox("Madinah Hotel (Visa Log)", options=madinah_options, key="v_mad")
        final_madinah = st.text_input("Type Madinah Hotel:") if sel_madinah == "Other (Manual Entry)" else sel_madinah

    col_dep, col_arr = st.columns(2)
    with col_dep:
        date_dep = st.date_input("Departure Date")
    with col_arr:
        date_arr = st.date_input("Arrival Date")

    st.markdown("<hr>", unsafe_allow_html=True)
    visa_file = st.file_uploader("Upload Visa Document (PDF/Image)", type=["pdf", "jpg", "png"], key="visa_up")
    if visa_file is not None:
        T.file_chips(st, [visa_file])

    if st.button("🚀 Extract Visa & Sync to Cloud", type="primary"):
        if visa_file is None:
            T.note(st, "bad", "<b>Upload a Visa document first!</b>")
        elif "Select" in final_agent or "Select" in final_transport or "Select" in final_visa_comp:
            T.note(st, "warn", "<b>Please fully select or type Agent, Transport, and Visa Company.</b>")
        elif not final_agent or not final_transport or not final_visa_comp:
            T.note(st, "warn", "<b>Manual entry fields cannot be empty!</b>")
        elif not gsheet_url or "spreadsheets/d" not in gsheet_url:
            T.note(st, "bad", "<b>Please paste your valid Google Sheet URL at the top!</b>")
        else:
            with st.spinner("Extracting Visa Data & Syncing to Google Sheets..."):
                try:
                    api_key = _get_gemini_api_key()
                    v_extractor = VisaExtractor(api_key)
                    db_logger = ExcelLogger()

                    visa_data = v_extractor.extract(visa_file)

                    full_log_data = {
                        "AGENT NAME": final_agent,
                        "VISA NUMBER": visa_data.get("VISA NUMBER", "N/A"),
                        "PASSPORT NUMBER": visa_data.get("PASSPORT NUMBER", "N/A"),
                        "NAME": visa_data.get("NAME", "N/A"),
                        "DEPARTURE DATE": date_dep.strftime("%d-%b-%Y"),
                        "ARRIVAL DATE": date_arr.strftime("%d-%b-%Y"),
                        "MAKKAH HOTEL": final_makkah,
                        "MEDINAH HOTEL": final_madinah,
                        "TRANSPORTATION": final_transport,
                        "VISA COMPANY": final_visa_comp
                    }

                    # Log directly to Google Sheets!
                    df_updated = db_logger.log_visa(full_log_data, sheet_url=gsheet_url)
                    T.note(st, "ok", f"<b>Successfully synced {visa_data.get('NAME')} to the Master Database!</b>")

                    try:
                        serial = str(df_updated.iloc[-1]["SERIAL NUMBER"])
                    except Exception:
                        serial = "—"
                    T.facts(st, [
                        ("SERIAL NUMBER", serial),
                        ("NAME", visa_data.get("NAME", "—")),
                        ("PASSPORT NUMBER", visa_data.get("PASSPORT NUMBER", "—")),
                        ("VISA NUMBER", visa_data.get("VISA NUMBER", "—")),
                    ])

                    # Display a quick preview on the screen
                    T.section(st, "", "Cloud Database Preview (Last 5 Entries)")
                    st.dataframe(df_updated.tail(5), use_container_width=True, hide_index=True)

                except Exception as e:
                    T.note(st, "bad", f"<b>Cloud syncing failed:</b> {e}")
