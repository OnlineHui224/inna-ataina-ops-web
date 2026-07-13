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
            df_existing = pd.read_excel(self.excel_path, dtype=str) # Force everything to stay as text
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        # 2. Auto-stamp today's date
        data_dict["DATE"] = datetime.now().strftime("%d-%b-%Y")
        
        # 3. Match the AI data to your columns safely and force string type
        row_data = {col: str(data_dict.get(col, "")).strip() for col in self.columns}
        df_new = pd.DataFrame([row_data])

        # 4. Append the new passenger to the bottom row
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # 5. Save the updated Excel sheet with professional column auto-spacing
        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
        
        # We use an ExcelWriter with openpyxl to dynamically adjust columns
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            df_combined.to_excel(writer, index=False, sheet_name="Visas")
            
            # Access the underlying openpyxl worksheet object
            worksheet = writer.sheets["Visas"]
            
            # Loop through each column, find the longest text, and set the perfect width
            for col in worksheet.columns:
                max_len = 0
                col_letter = col[0].column_letter # Get column letter (A, B, C...)
                
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                
                # Set width with some extra breathing room padding (+ 4 spaces)
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
        return self.excel_path
