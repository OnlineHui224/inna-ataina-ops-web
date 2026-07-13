import os
import pandas as pd
from datetime import datetime
from src.core.logger import logger

class ExcelLogger:
    def __init__(self, excel_path="output/Master_Visa_Log.xlsx"):
        self.excel_path = excel_path
        
        # These perfectly match the screenshot you provided
        self.columns = [
            "DATE", "AGENT NAME", "VISA NUMBER", "PASSPORT NUMBER", 
            "NAME", "DEPARTURE DATE", "ARRIVAL DATE", 
            "MAKKAH HOTEL", "MEDINAH HOTEL", "TRANSPORTATION", "VISA COMPANY"
        ]

    def log_visa(self, extracted_data: dict) -> str:
        """Appends new passenger data to the master Excel file."""
        logger.info(f"Logging new visa entry to {self.excel_path}...")
        
        # 1. Open the existing Master File (or create it if it's the first time)
        if os.path.exists(self.excel_path):
            df_existing = pd.read_excel(self.excel_path)
        else:
            df_existing = pd.DataFrame(columns=self.columns)

        # 2. Automatically generate today's date for the 'DATE' column
        extracted_data["DATE"] = datetime.now().strftime("%d-%b-%Y")

        # 3. Match the AI's extracted data to your exact column headers
        # If a piece of data is missing, it safely leaves the cell blank ("")
        row_data = {col: extracted_data.get(col, "") for col in self.columns}
        
        # Convert the single row into a Pandas table
        df_new = pd.DataFrame([row_data])

        # 4. Attach the new row to the bottom of the existing master table
        # ignore_index=True ensures the row numbers stay in perfect order (1, 2, 3...)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)

        # 5. Save the updated table back over the original file
        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
        df_combined.to_excel(self.excel_path, index=False)
        
        logger.info("Successfully updated Master Visa Log.")
        return self.excel_path
