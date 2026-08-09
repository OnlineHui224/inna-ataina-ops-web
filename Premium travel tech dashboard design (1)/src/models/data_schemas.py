from pydantic import BaseModel, Field
from typing import List, Optional

class FlightSegment(BaseModel):
    departure_city: str = Field(description="Departure airport code or city")
    arrival_city: str = Field(description="Arrival airport code or city")
    date: str = Field(description="Date of flight (e.g., 23 JUL)")
    departure_time: str = Field(description="Time of departure")
    arrival_time: str = Field(description="Time of arrival")
    carrier: str = Field(description="Airline name")
    flight_number: str = Field(description="Flight number (e.g., ET 0940)")

class TicketData(BaseModel):
    passenger_name: str = Field(description="Primary passenger full name")
    adults: int = Field(default=1, description="Total number of adults")
    children: int = Field(default=0, description="Total number of children/infants")
    pnr: str = Field(description="Booking reference or PNR")
    primary_carrier: str = Field(description="Main airline for the journey")
    flights: List[FlightSegment] = Field(description="List of all flight segments in chronological order")
    ai_confidence: float = Field(default=1.0, description="AI confidence score from 0.0 to 1.0")

    @property
    def total_pax(self) -> int:
        return self.adults + self.children