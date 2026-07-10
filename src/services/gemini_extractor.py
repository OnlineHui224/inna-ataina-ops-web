import os
import json
from typing import Any, Dict, List
import google.generativeai as genai
from pydantic import ValidationError

from src.core.logger import logger
from src.models.data_schemas import TicketData

class GeminiExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""
        self.last_error = ""
        
        if not self.api_key:
            logger.error("No API key provided to GeminiExtractor.")
            raise ValueError("Gemini API key is missing.")

        # Configure the generative AI framework with your key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    @staticmethod
    def _ticket_data_response_schema() -> Dict[str, Any]:
        """Gemini response schema aligned with TicketData/FlightSegment."""
        return {
            "type": "object",
            "properties": {
                "passenger_name": {"type": "string"},
                "adults": {"type": "integer"},
                "children": {"type": "integer"},
                "pnr": {"type": "string"},
                "primary_carrier": {"type": "string"},
                "flights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "departure_city": {"type": "string"},
                            "arrival_city": {"type": "string"},
                            "date": {"type": "string"},
                            "departure_time": {"type": "string"},
                            "arrival_time": {"type": "string"},
                            "carrier": {"type": "string"},
                            "flight_number": {"type": "string"},
                        },
                        "required": [
                            "departure_city", "arrival_city", "date", 
                            "departure_time", "arrival_time", "carrier", "flight_number"
                        ],
                    },
                },
                "ai_confidence": {"type": "number"},
            },
            "required": [
                "passenger_name", "adults", "children", "pnr", 
                "primary_carrier", "flights", "ai_confidence"
            ],
        }

    @staticmethod
    def _build_prompt() -> str:
        return (
            "You are a master travel data extractor. I have provided one or more travel document files for a single trip. \n"
            "Your job is to read ALL of the provided files together as one continuous journey.\n"
            "Return ONLY JSON matching the response schema.\n"
            "Rules:\n"
            "1) Find the primary passenger's name and PNR.\n"
            "2) Extract EVERY flight leg from ALL files and keep flights in chronological order.\n"
            "3) Use exact field names from schema, do not add unknown keys.\n"
            "4) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
            "5) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
            "6) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
        )

    @staticmethod
    def _safe_json_loads(raw_text: str) -> Dict[str, Any]:
        """Safely parse JSON text. Handles occasional markdown fences defensively."""
        text = (raw_text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc

    def extract(self, uploaded_files) -> TicketData:
        """Handles MULTIPLE uploaded files by passing raw content directly inline."""
        logger.info(f"Starting direct contents extraction for {len(uploaded_files)} file(s)...")
        
        contents = [self._build_prompt()]

        try:
            # Loop through files and convert them to direct binary data parts for the model
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.getvalue()
                mime_type = uploaded_file.type  # Automatically detects application/pdf, image/png, etc.
                
                contents.append({
                    "mime_type": mime_type,
                    "data": file_bytes
                })

            generation_config = genai.GenerationConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=self._ticket_data_response_schema(),
            )

            # Send everything inline—bypassing the Cloud File Manager permission checks entirely
            response = self.model.generate_content(
                contents,
                generation_config=generation_config
            )

            raw_text = getattr(response, "text", "") or ""
            if not raw_text:
                raise ValueError("Gemini returned an empty response. The tickets might be unreadable.")

            raw_data = self._safe_json_loads(raw_text)
            validated_data = TicketData(**raw_data)

            logger.info("Successfully extracted multi-file data via inline stream.")
            return validated_data

        except ValidationError as exc:
            logger.error("Pydantic validation failed: %s", exc)
            raise ValueError(f"Extracted data failed schema validation: {exc}") from exc
        except Exception as exc:
            logger.error("Direct inline extraction failed: %s", exc)
            raise
