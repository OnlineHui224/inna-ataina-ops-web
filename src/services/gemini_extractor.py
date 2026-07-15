import os
import json
import base64
import requests
from typing import Any, Dict
from pydantic import ValidationError

from src.core.logger import logger
from src.models.data_schemas import TicketData

class GeminiExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""
        
        if not self.api_key:
            logger.error("No API key provided.")
            raise ValueError("Gemini API key is missing.")

    @staticmethod
    def _ticket_data_response_schema() -> Dict[str, Any]:
        """Strict OpenAPI Schema for the raw REST API."""
        return {
            "type": "OBJECT",
            "properties": {
                "passenger_name": {"type": "STRING"},
                "adults": {"type": "INTEGER"},
                "children": {"type": "INTEGER"},
                "pnr": {"type": "STRING"},
                "primary_carrier": {"type": "STRING"},
                "flights": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "departure_city": {"type": "STRING"},
                            "arrival_city": {"type": "STRING"},
                            "date": {"type": "STRING"},
                            "departure_time": {"type": "STRING"},
                            "arrival_time": {"type": "STRING"},
                            "carrier": {"type": "STRING"},
                            "flight_number": {"type": "STRING"},
                        },
                        "required": [
                            "departure_city", "arrival_city", "date", 
                            "departure_time", "arrival_time", "carrier", "flight_number"
                        ]
                    }
                },
                "ai_confidence": {"type": "NUMBER"}
            },
            "required": [
                "passenger_name", "adults", "children", "pnr", 
                "primary_carrier", "flights", "ai_confidence"
            ]
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
            "5) Convert all airline carrier names into standard 2-letter IATA airline codes.\n"
            "6) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes.\n"
        )

    def extract(self, uploaded_files) -> TicketData:
        """Bypasses the deprecated library and connects directly to Google's REST API."""
        logger.info(f"Starting direct REST API extraction for {len(uploaded_files)} file(s)...")
        
        parts = [{"text": self._build_prompt()}]

        try:
            # 1. Convert all uploaded files into raw binary data
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.getvalue()
                mime_type = uploaded_file.type
                b64_data = base64.b64encode(file_bytes).decode("utf-8")
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": b64_data
                    }
                })

            # 2. Package the exact payload
