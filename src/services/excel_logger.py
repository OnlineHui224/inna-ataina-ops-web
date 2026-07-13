import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

class ExcelLogger:
    def __init__(self):
        # Initializes the secure connection to Google Sheets using your Secrets
        self.conn = st.connection("gsheets", type=GSheetsConnection)
        
        self.columns = [
            "SERIAL NUMBER", "AGENT NAME", "VISA NUMBER", "PASSPORT NUMBER", 
            "NAME", "DEPARTURE DATE", "ARRIVAL DATE", 
            "MAKKAH HOTEL", "MEDINAH HOTEL", "TRANSPORTATION", "VISA COMPANY"
        ]
        
        # The Master Dictionary of Agent Prefixes
        self.agent_prefixes = {
            "Inna-Ataina": "INNA", "AshTag": "ASH", "Al-Mubarak": "MUB", 
            "Seriki Group": "SER", "Soaif Travel": "SOA", "Mukareem": "MUK", 
            "AL-Lagusyy": "LAG", "Al-Wafah": "WAF", "Travel nest": "NES", 
            "AT-Tibyan": "TIB", "AL-Haqq": "HAQ", "AL-Bushrah": "BUS", 
            "AL-Shambagy": "SHA", "Portfolio (Musty)": "POR", "AL-furqan": "FUR", 
            "Baseeroh": "BAS", "Alh-Adua agba": "ADU", "Nurul-qulub": "NUR", 
            "Nokbah": "NOK", "Al-Jannah Travels": "JAN", "Voyagemistry": "VOY", 
            "Umrah UK": "UMR", "Saheed": "SAH", "WakaNow": "WAK", "Chiroma": "CHI"
        }

    def _generate_serial_number(self, agent_name: str, df_existing: pd.DataFrame) -> str:
        """Reads the live cloud sheet to find the true, absolute highest serial number."""
        prefix = self.agent_prefixes.get(agent_name)
        
        if not prefix:
            clean_name = re.sub(r'[^A-Za-z]', '', agent_name).upper()
            prefix = clean_name[:4] if len(clean_name) >= 4 else clean_name.ljust(3, 'X')
        
        if df_existing.empty or "SERIAL NUMBER" not in df_existing.columns:
            return f"{prefix}001"
        
        serials = df_existing["SERIAL NUMBER"].dropna().astype(str)
        matching_serials = serials[serials.str.startswith(prefix)]
        
        if matching_serials.empty:
            return f"{prefix}001"
        
        max_num = 0
        for s in matching_serials:
            match = re.search(r'(\d+)$', s)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        
        return f"{prefix}{(max_num + 1):03d}"

    def log_visa(self, data_dict: dict, sheet_url: str):
        """Pulls the live cloud sheet, appends data, and updates it instantly."""
        # 1. Read directly from the Live Google Sheet
        try:
            df_existing = self.conn.read(spreadsheet=sheet_url, ttl=0) 
            df_existing = df_existing.dropna(how='all')
        except Exception:
            df_existing = pd.DataFrame(columns=self.columns)

        # 2. Generate the Serial Number based on true cloud totals
        final_agent = data_dict.get("AGENT NAME", "UNKNOWN")
        data_dict["SERIAL NUMBER"] = self._generate_serial_number(final_agent, df_existing)
        
        # 3. Format the row cleanly
        row_data = {col: str(data_dict.get(col, "")).strip() for col in self.columns}
        df_new = pd.DataFrame([row_data])
        
        # 4. Combine existing data with the new entry
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # 5. Push the data straight back up to the Google Sheet cloud
        self.conn.update(spreadsheet=sheet_url, data=df_combined)
        return df_combined
