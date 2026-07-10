import os
import json
import tempfile
from typing import Any, Dict, List
import google.generativeai as genai
from pydantic import ValidationError

from src.core.logger import logger
from src.models.data_schemas import TicketData

class GeminiExtractor:
    def __init__(self, api_key: str):
        # 1. Clean the API key of any accidental hidden spaces or quotes
        self.api_key = api_key.strip() if api_key else ""
        self.last_error = ""
        
        if not self.api_key:
            logger.error("No API key provided to GeminiExtractor.")
            raise ValueError("Gemini API key is missing.")

        # 2. CRITICAL FIX: Explicitly configure the API key right here.
        genai.configure(api_key=self.api_key)
        
        # 3. Initialize the generative model
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
        """Handles MULTIPLE Streamlit UploadedFile objects at once."""
        logger.info(f"Starting AI extraction for {len(uploaded_files)} file(s)...")
        
        gemini_uploaded_files = []
        temp_file_paths = []

        try:
            # 1. Loop through every file the user uploaded
            for uploaded_file in uploaded_files:
                # Save each file temporarily so Gemini can read it natively
                suffix = os.path.splitext(uploaded_file.name)[1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_paths.append(temp_file.name)
                
                # Upload each file directly to Google's AI servers
                gemini_file = genai.upload_file(path=temp_file_paths[-1])
                gemini_uploaded_files.append(gemini_file)

            # 2. Tell the AI to merge everything (Prompt + List of Files)
            content_to_send = [self._build_prompt()] + gemini_uploaded_files
            
            generation_config = genai.GenerationConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=self._ticket_data_response_schema(),
            )

            # 3. Call the Model
            response = self.model.generate_content(
                content_to_send,
                generation_config=generation_config
            )

            raw_text = getattr(response, "text", "") or ""
            if not raw_text:
                raise ValueError("Gemini returned an empty response. The tickets might be unreadable.")

            # 4. Parse and Validate
            raw_data = self._safe_json_loads(raw_text)
            validated_data = TicketData(**raw_data)

            logger.info("Successfully extracted and merged multi-file data.")
            return validated_data

        except ValidationError as exc:
            logger.error("Pydantic validation failed: %s", exc)
            raise ValueError(f"Extracted data failed schema validation: {exc}") from exc
        except Exception as exc:
            logger.error("Extraction failed: %s", exc)
            raise
        finally:
            # 5. Clean up: Delete temporary files so your server stays clean
            for path in temp_file_paths:
                if os.path.exists(path):
                    os.remove(path)
            # Clean up Google Cloud memory
            for g_file in gemini_uploaded_files:
                try:
                    genai.delete_file(g_file.name)
                except:
                    pass
