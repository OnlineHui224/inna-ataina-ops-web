import os
import pandas as pd
from datetime import datetime

class ExcelLogger:
    def __init__(self, excel_path="output/contract_visas_documentation.xlsx"):
        self.excel_path = excel_path
        
        # Columns perfectly matched to your Excel screenshot
        self.columns = [
            "DATE", "AGENT NAME", "VISA NUMBER", "PASSPORT NUMBER", 
            "NAME", "DEPARTURE DATE", "ARRIVAL DATE", 
            "MAKKAH HOTEL", "MEDINAH HOTEL", "TRANSPORTATION", "VISA COMPANY"
        ]

    def log_visa(self, data_dict: dict):
        # 1. Open the existing Excel file, or create a blank one
        if os.path.exists(self.excel_path):
            df_existing = pd.read_excel(self.excel_path)
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        # 2. Auto-stamp today's date
        data_dict["DATE"] = datetime.now().strftime("%d-%b-%Y")
        
        # 3. Match the AI data to your columns safely
        row_data = {col: data_dict.get(col, "") for col in self.columns}
        df_new = pd.DataFrame([row_data])

        # 4. Append the new passenger to the bottom row
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # 5. Save the updated Excel sheet
        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
        df_combined.to_excel(self.excel_path, index=False)
        
        return self.excel_path
