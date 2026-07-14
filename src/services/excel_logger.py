import pandas as pd
import os
import re

class ExcelLogger:
    def __init__(self, filename="visa_data.csv"):
        self.filename = filename
        
        self.columns = [
            "SERIAL NUMBER", "AGENT NAME", "VISA NUMBER", "PASSPORT NUMBER", 
            "NAME", "DEPARTURE DATE", "ARRIVAL DATE", 
            "MAKKAH HOTEL", "MEDINAH HOTEL", "TRANSPORTATION", "VISA COMPANY"
        ]
        
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

    def log_visa(self, data_dict: dict, sheet_url: str = None):
        """Logs to local CSV instead of Google Sheets."""
        # 1. Read existing local CSV
        if os.path.exists(self.filename):
            df_existing = pd.read_csv(self.filename)
            df_existing = df_existing.dropna(how='all')
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        # 2. Generate Serial Number (logic untouched)
        final_agent = data_dict.get("AGENT NAME", "UNKNOWN")
        data_dict["SERIAL NUMBER"] = self._generate_serial_number(final_agent, df_existing)
        
        # 3. Format the row
        row_data = {col: str(data_dict.get(col, "")).strip() for col in self.columns}
        df_new = pd.DataFrame([row_data])
        
        # 4. Append and save locally
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(self.filename, index=False)
        
        return df_combined
