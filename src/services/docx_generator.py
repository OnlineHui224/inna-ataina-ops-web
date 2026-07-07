from docx import Document
import os
from src.models.data_schemas import TicketData
from src.core.logger import logger

class DocxGenerator:
    def __init__(self, template_path: str, output_dir: str):
        self.template_path = template_path
        self.output_dir = output_dir

    def _safe_write_cell(self, cell, text):
        """Writes text to a cell while attempting to preserve paragraph styles."""
        if not cell: return
        cell.text = str(text)
        # Apply standard formatting if needed, though template defaults usually hold
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Arial' # Standardizing based on observed template

    def generate(self, data: TicketData) -> str:
        logger.info("Starting DOCX generation...")
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template not found at {self.template_path}")
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        doc = Document(self.template_path)

        # 1. Header Injection (FLIGHT: <<CARRIER>> – MEDINAH)
        for p in doc.paragraphs:
            if "FLIGHT:" in p.text and "MEDINAH" in p.text:
                p.text = f"FLIGHT: {data.primary_carrier.upper()} – MEDINAH"

        # 2. Table 1: Passenger Totals (Index 0)
        if len(doc.tables) > 0:
            table_pax = doc.tables[0]
            # Assuming Row 2 contains the entry cells based on the blank template mapping
            if len(table_pax.rows) > 2:
                self._safe_write_cell(table_pax.cell(2, 2), data.adults)    # Adult
                self._safe_write_cell(table_pax.cell(2, 3), data.children)  # Child
                self._safe_write_cell(table_pax.cell(2, 4), data.total_pax) # Total

        # 3. Table 2: Flights (Index 1)
        if len(doc.tables) > 1:
            table_flights = doc.tables[1]
            start_row = 2 # Based on template header rows
            
            for idx, flight in enumerate(data.flights):
                row_idx = start_row + idx
                # If we exceed pre-built rows, add a new one
                if row_idx >= len(table_flights.rows):
                    table_flights.add_row()
                
                row = table_flights.rows[row_idx]
                self._safe_write_cell(row.cells[0], flight.departure_city)
                self._safe_write_cell(row.cells[1], flight.arrival_city)
                
                # Handling the pre-existing "2026" string logic
                date_str = f"{flight.date} 2026" if "2026" not in flight.date else flight.date
                self._safe_write_cell(row.cells[2], date_str)
                
                self._safe_write_cell(row.cells[3], flight.departure_time)
                self._safe_write_cell(row.cells[4], flight.arrival_time)
                self._safe_write_cell(row.cells[5], flight.carrier)
                self._safe_write_cell(row.cells[6], flight.flight_number)
                
                # Only write PNR on the first row to avoid clutter, or write on all
                if idx == 0:
                    self._safe_write_cell(row.cells[7], data.pnr)

        # Ensure safe filename
        safe_name = "".join([c for c in data.passenger_name if c.isalpha() or c.isspace()]).rstrip()
        filename = f"{safe_name.replace(' ', '_')}_Itinerary.docx"
        output_path = os.path.join(self.output_dir, filename)
        
        doc.save(output_path)
        logger.info(f"DOCX saved successfully at {output_path}")
        
        return output_path