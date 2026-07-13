import os
import pandas as pd
import re

class ExcelLogger:
    def __init__(self, excel_path="output/contract_visas_documentation.xlsx"):
        self.excel_path = excel_path
        
        # Changed "DATE" to "SERIAL NUMBER"
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
            "Umrah UK": "UMR"
        }

    def _generate_serial_number(self, agent_name: str, df_existing: pd.DataFrame) -> str:
        """Finds the agent prefix, checks the Excel file, and adds 1 to the highest count."""
        prefix = self.agent_prefixes.get(agent_name)
        
        # If it's a brand new custom agent, auto-generate a 4-letter prefix
        if not prefix:
            clean_name = re.sub(r'[^A-Za-z]', '', agent_name).upper()
            prefix = clean_name[:4] if len(clean_name) >= 4 else clean_name.ljust(3, 'X')
        
        if df_existing.empty or "SERIAL NUMBER" not in df_existing.columns:
            return f"{prefix}001"
        
        # Search the database for all serial numbers matching this prefix
        serials = df_existing["SERIAL NUMBER"].dropna().astype(str)
        matching_serials = serials[serials.str.startswith(prefix)]
        
        if matching_serials.empty:
            return f"{prefix}001"
        
        # Find the highest number and add 1
        max_num = 0
        for s in matching_serials:
            match = re.search(r'(\d+)$', s)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        
        next_num = max_num + 1
        return f"{prefix}{next_num:03d}"

    def log_visa(self, data_dict: dict):
        if os.path.exists(self.excel_path):
            df_existing = pd.read_excel(self.excel_path, dtype=str)
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        # Generate the smart serial number
        final_agent = data_dict.get("AGENT NAME", "UNKNOWN")
        data_dict["SERIAL NUMBER"] = self._generate_serial_number(final_agent, df_existing)
        
        row_data = {col: str(data_dict.get(col, "")).strip() for col in self.columns}
        df_new = pd.DataFrame([row_data])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
        
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            df_combined.to_excel(writer, index=False, sheet_name="Visas")
            worksheet = writer.sheets["Visas"]
            for col in worksheet.columns:
                max_len = 0
                col_letter = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 15)
        
        return self.excel_path
