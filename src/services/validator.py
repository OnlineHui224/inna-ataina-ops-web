from src.models.data_schemas import TicketData
from src.core.logger import logger

class DataValidator:
    @staticmethod
    def validate(data: TicketData) -> List[str]:
        warnings = []
        
        if not data.passenger_name:
            warnings.append("Passenger name is missing.")
            
        if not data.pnr:
            warnings.append("PNR/Booking Reference is missing.")
            
        if not data.flights:
            warnings.append("No flights were extracted from the document.")
            
        if data.total_pax == 0:
            warnings.append("Passenger count is zero.")
            
        # Check chronology and return flights
        if len(data.flights) == 1:
            warnings.append("Only a one-way flight detected. Missing return flight.")
            
        logger.info(f"Validation complete. Found {len(warnings)} warnings.")
        return warnings