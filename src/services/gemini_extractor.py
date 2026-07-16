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
        # Reverted to securely reading the API key, no hardcoding.
        self.api_key = api_key.strip() if api_key else ""
        
        if not self.api_key:
            logger.error("No API key provided.")
            raise ValueError("Gemini API key is missing.")

    @staticmethod
    def _ticket_data_response_schema() -> Dict[str, Any]:
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
        logger.info(f"Starting direct REST API extraction for {len(uploaded_files)} file(s)...")
        
        parts = [{"text": self._build_prompt()}]

        try:
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

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": 0.0,
                    "responseMimeType": "application/json",
                    "responseSchema": self._ticket_data_response_schema()
                }
            }

            # Back to the original URL
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            
            # Back to the original Headers
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Google API Error Code {response.status_code}: {response.text}")
                raise ValueError(f"Google API returned error status {response.status_code}. Details: {response.text}")
                
            data = response.json()
            
            if "candidates" not in data:
                logger.error(f"Google API Response missing 'candidates'. Full response: {data}")
                raise ValueError(f"Google API rejected request. Details: {data}")

            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            if not raw_text:
                raise ValueError("Gemini returned an empty response.")

            text = raw_text.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:].strip()

            raw_json = json.loads(text)
            validated_data = TicketData(**raw_json)

            logger.info("Successfully extracted multi-file data via REST.")
            return validated_data

        except requests.exceptions.RequestException as exc:
            err_msg = str(exc)
            if exc.response is not None:
                err_msg += f" Response: {exc.response.text}"
            logger.error("REST API extraction failed: %s", err_msg)
            raise ValueError(f"API Request failed: {err_msg}") from exc
        except ValidationError as exc:
            logger.error("Pydantic validation failed: %s", exc)
            raise ValueError(f"Extracted data failed schema validation: {exc}") from exc
        except Exception as exc:
            logger.error("Extraction failed: %s", exc)
            raise
