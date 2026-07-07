import os  # <--- JUST ADD THIS LINE AT THE VERY TOP
import json
from typing import Any, Dict, List
import google.generativeai as genai
import PyPDF2
from PIL import Image
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
        # This overrides Streamlit's environment and forces it to use your exact key.
        genai.configure(api_key=self.api_key)
        
        # 3. Initialize the generative model
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    @staticmethod
    def _extract_text_from_pdf(pdf_path: str) -> str:
        text_chunks: List[str] = []

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)

        return "\n".join(text_chunks).strip()

    @staticmethod
    def _ticket_data_response_schema() -> Dict[str, Any]:
        """
        Gemini response schema aligned with TicketData/FlightSegment.

        This forces the model to return the exact keys and structure.
        """
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
                            "departure_city",
                            "arrival_city",
                            "date",
                            "departure_time",
                            "arrival_time",
                            "carrier",
                            "flight_number",
                        ],
                    },
                },
                "ai_confidence": {"type": "number"},
            },
            "required": [
                "passenger_name",
                "adults",
                "children",
                "pnr",
                "primary_carrier",
                "flights",
                "ai_confidence",
            ],
        }

    @staticmethod
    def _build_prompt() -> str:
        return (
            "You are a travel ticket extraction engine.\n"
            "Extract itinerary and passenger details from the provided document.\n"
            "Return ONLY JSON matching the response schema.\n"
            "Rules:\n"
            "1) Use exact field names from schema.\n"
            "2) Do not add unknown keys.\n"
            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
            "4) Keep flights in chronological order.\n"
            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
            "6) ai_confidence must be between 0.0 and 1.0.\n"
            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
        )

    @staticmethod
    def _safe_json_loads(raw_text: str) -> Dict[str, Any]:
        """
        Safely parse JSON text. Handles occasional markdown fences defensively.
        """
        text = (raw_text or "").strip()

        if text.startswith("```"):
            # Remove markdown fences if model ever returns them.
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc

    def process_document(self, file_path: str) -> TicketData:
        logger.info("Starting AI extraction for: %s", file_path)

        _, ext = os.path.splitext(file_path.lower())

        if ext == ".pdf":
            content = self._extract_text_from_pdf(file_path)
            if not content:
                raise ValueError("No text could be extracted from PDF.")
        elif ext in {".png", ".jpg", ".jpeg"}:
            content = Image.open(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        generation_config = genai.GenerationConfig(
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=self._ticket_data_response_schema(),
        )

        try:
            response = self.model.generate_content(
                [self._build_prompt(), content],
                generation_config=generation_config,
            )

            raw_text = getattr(response, "text", "") or ""
            if not raw_text:
                raise ValueError("Gemini returned an empty response.")

            raw_data = self._safe_json_loads(raw_text)

            # Final strict guardrail: Pydantic validation.
            validated_data = TicketData(**raw_data)

            logger.info("AI extraction successful and schema-validated.")
            return validated_data

        except ValidationError as exc:
            logger.error("Pydantic validation failed: %s", exc)
            raise ValueError(f"Extracted data failed schema validation: {exc}") from exc
        except Exception as exc:
            logger.error("Extraction failed: %s", exc)
            @staticmethod
            def _build_prompt() -> str:
                return (
                    "You are a travel ticket extraction engine.\n"
                    "Extract itinerary and passenger details from the provided document.\n"
                    "Return ONLY JSON matching the response schema.\n"
                    "Rules:\n"
                    "1) Use exact field names from schema.\n"
                    "2) Do not add unknown keys.\n"
                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                    "4) Keep flights in chronological order.\n"
                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                )                @staticmethod
                def _build_prompt() -> str:
                    return (
                        "You are a travel ticket extraction engine.\n"
                        "Extract itinerary and passenger details from the provided document.\n"
                        "Return ONLY JSON matching the response schema.\n"
                        "Rules:\n"
                        "1) Use exact field names from schema.\n"
                        "2) Do not add unknown keys.\n"
                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                        "4) Keep flights in chronological order.\n"
                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                    )                    @staticmethod
                    def _build_prompt() -> str:
                        return (
                            "You are a travel ticket extraction engine.\n"
                            "Extract itinerary and passenger details from the provided document.\n"
                            "Return ONLY JSON matching the response schema.\n"
                            "Rules:\n"
                            "1) Use exact field names from schema.\n"
                            "2) Do not add unknown keys.\n"
                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                            "4) Keep flights in chronological order.\n"
                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                        )                        @staticmethod
                        def _build_prompt() -> str:
                            return (
                                "You are a travel ticket extraction engine.\n"
                                "Extract itinerary and passenger details from the provided document.\n"
                                "Return ONLY JSON matching the response schema.\n"
                                "Rules:\n"
                                "1) Use exact field names from schema.\n"
                                "2) Do not add unknown keys.\n"
                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                "4) Keep flights in chronological order.\n"
                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                            )                            @staticmethod
                            def _build_prompt() -> str:
                                return (
                                    "You are a travel ticket extraction engine.\n"
                                    "Extract itinerary and passenger details from the provided document.\n"
                                    "Return ONLY JSON matching the response schema.\n"
                                    "Rules:\n"
                                    "1) Use exact field names from schema.\n"
                                    "2) Do not add unknown keys.\n"
                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                    "4) Keep flights in chronological order.\n"
                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                )                                @staticmethod
                                def _build_prompt() -> str:
                                    return (
                                        "You are a travel ticket extraction engine.\n"
                                        "Extract itinerary and passenger details from the provided document.\n"
                                        "Return ONLY JSON matching the response schema.\n"
                                        "Rules:\n"
                                        "1) Use exact field names from schema.\n"
                                        "2) Do not add unknown keys.\n"
                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                        "4) Keep flights in chronological order.\n"
                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                    )                                    @staticmethod
                                    def _build_prompt() -> str:
                                        return (
                                            "You are a travel ticket extraction engine.\n"
                                            "Extract itinerary and passenger details from the provided document.\n"
                                            "Return ONLY JSON matching the response schema.\n"
                                            "Rules:\n"
                                            "1) Use exact field names from schema.\n"
                                            "2) Do not add unknown keys.\n"
                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                            "4) Keep flights in chronological order.\n"
                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                        )                                        @staticmethod
                                        def _build_prompt() -> str:
                                            return (
                                                "You are a travel ticket extraction engine.\n"
                                                "Extract itinerary and passenger details from the provided document.\n"
                                                "Return ONLY JSON matching the response schema.\n"
                                                "Rules:\n"
                                                "1) Use exact field names from schema.\n"
                                                "2) Do not add unknown keys.\n"
                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                "4) Keep flights in chronological order.\n"
                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                            )                                            @staticmethod
                                            def _build_prompt() -> str:
                                                return (
                                                    "You are a travel ticket extraction engine.\n"
                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                    "Return ONLY JSON matching the response schema.\n"
                                                    "Rules:\n"
                                                    "1) Use exact field names from schema.\n"
                                                    "2) Do not add unknown keys.\n"
                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                    "4) Keep flights in chronological order.\n"
                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                )                                                @staticmethod
                                                def _build_prompt() -> str:
                                                    return (
                                                        "You are a travel ticket extraction engine.\n"
                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                        "Return ONLY JSON matching the response schema.\n"
                                                        "Rules:\n"
                                                        "1) Use exact field names from schema.\n"
                                                        "2) Do not add unknown keys.\n"
                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                        "4) Keep flights in chronological order.\n"
                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                    )                                                    @staticmethod
                                                    def _build_prompt() -> str:
                                                        return (
                                                            "You are a travel ticket extraction engine.\n"
                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                            "Return ONLY JSON matching the response schema.\n"
                                                            "Rules:\n"
                                                            "1) Use exact field names from schema.\n"
                                                            "2) Do not add unknown keys.\n"
                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                            "4) Keep flights in chronological order.\n"
                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                        )                                                        @staticmethod
                                                        def _build_prompt() -> str:
                                                            return (
                                                                "You are a travel ticket extraction engine.\n"
                                                                "Extract itinerary and passenger details from the provided document.\n"
                                                                "Return ONLY JSON matching the response schema.\n"
                                                                "Rules:\n"
                                                                "1) Use exact field names from schema.\n"
                                                                "2) Do not add unknown keys.\n"
                                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                "4) Keep flights in chronological order.\n"
                                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                            )                                                            @staticmethod
                                                            def _build_prompt() -> str:
                                                                return (
                                                                    "You are a travel ticket extraction engine.\n"
                                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                                    "Return ONLY JSON matching the response schema.\n"
                                                                    "Rules:\n"
                                                                    "1) Use exact field names from schema.\n"
                                                                    "2) Do not add unknown keys.\n"
                                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                    "4) Keep flights in chronological order.\n"
                                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                )                                                                @staticmethod
                                                                def _build_prompt() -> str:
                                                                    return (
                                                                        "You are a travel ticket extraction engine.\n"
                                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                                        "Return ONLY JSON matching the response schema.\n"
                                                                        "Rules:\n"
                                                                        "1) Use exact field names from schema.\n"
                                                                        "2) Do not add unknown keys.\n"
                                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                        "4) Keep flights in chronological order.\n"
                                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                    )                                                                    @staticmethod
                                                                    def _build_prompt() -> str:
                                                                        return (
                                                                            "You are a travel ticket extraction engine.\n"
                                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                                            "Return ONLY JSON matching the response schema.\n"
                                                                            "Rules:\n"
                                                                            "1) Use exact field names from schema.\n"
                                                                            "2) Do not add unknown keys.\n"
                                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                            "4) Keep flights in chronological order.\n"
                                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                        )                                                                        @staticmethod
                                                                        def _build_prompt() -> str:
                                                                            return (
                                                                                "You are a travel ticket extraction engine.\n"
                                                                                "Extract itinerary and passenger details from the provided document.\n"
                                                                                "Return ONLY JSON matching the response schema.\n"
                                                                                "Rules:\n"
                                                                                "1) Use exact field names from schema.\n"
                                                                                "2) Do not add unknown keys.\n"
                                                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                "4) Keep flights in chronological order.\n"
                                                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                            )                                                                            @staticmethod
                                                                            def _build_prompt() -> str:
                                                                                return (
                                                                                    "You are a travel ticket extraction engine.\n"
                                                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                                                    "Return ONLY JSON matching the response schema.\n"
                                                                                    "Rules:\n"
                                                                                    "1) Use exact field names from schema.\n"
                                                                                    "2) Do not add unknown keys.\n"
                                                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                    "4) Keep flights in chronological order.\n"
                                                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                )                                                                                @staticmethod
                                                                                def _build_prompt() -> str:
                                                                                    return (
                                                                                        "You are a travel ticket extraction engine.\n"
                                                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                                                        "Return ONLY JSON matching the response schema.\n"
                                                                                        "Rules:\n"
                                                                                        "1) Use exact field names from schema.\n"
                                                                                        "2) Do not add unknown keys.\n"
                                                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                        "4) Keep flights in chronological order.\n"
                                                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                    )                                                                                    @staticmethod
                                                                                    def _build_prompt() -> str:
                                                                                        return (
                                                                                            "You are a travel ticket extraction engine.\n"
                                                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                                                            "Return ONLY JSON matching the response schema.\n"
                                                                                            "Rules:\n"
                                                                                            "1) Use exact field names from schema.\n"
                                                                                            "2) Do not add unknown keys.\n"
                                                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                            "4) Keep flights in chronological order.\n"
                                                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                        )                                                                                        @staticmethod
                                                                                        def _build_prompt() -> str:
                                                                                            return (
                                                                                                "You are a travel ticket extraction engine.\n"
                                                                                                "Extract itinerary and passenger details from the provided document.\n"
                                                                                                "Return ONLY JSON matching the response schema.\n"
                                                                                                "Rules:\n"
                                                                                                "1) Use exact field names from schema.\n"
                                                                                                "2) Do not add unknown keys.\n"
                                                                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                "4) Keep flights in chronological order.\n"
                                                                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                            )                                                                                            @staticmethod
                                                                                            def _build_prompt() -> str:
                                                                                                return (
                                                                                                    "You are a travel ticket extraction engine.\n"
                                                                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                                                                    "Return ONLY JSON matching the response schema.\n"
                                                                                                    "Rules:\n"
                                                                                                    "1) Use exact field names from schema.\n"
                                                                                                    "2) Do not add unknown keys.\n"
                                                                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                    "4) Keep flights in chronological order.\n"
                                                                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                )                                                                                                @staticmethod
                                                                                                def _build_prompt() -> str:
                                                                                                    return (
                                                                                                        "You are a travel ticket extraction engine.\n"
                                                                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                                                                        "Return ONLY JSON matching the response schema.\n"
                                                                                                        "Rules:\n"
                                                                                                        "1) Use exact field names from schema.\n"
                                                                                                        "2) Do not add unknown keys.\n"
                                                                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                        "4) Keep flights in chronological order.\n"
                                                                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                    )                                                                                                    @staticmethod
                                                                                                    def _build_prompt() -> str:
                                                                                                        return (
                                                                                                            "You are a travel ticket extraction engine.\n"
                                                                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                                                                            "Return ONLY JSON matching the response schema.\n"
                                                                                                            "Rules:\n"
                                                                                                            "1) Use exact field names from schema.\n"
                                                                                                            "2) Do not add unknown keys.\n"
                                                                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                            "4) Keep flights in chronological order.\n"
                                                                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                        )                                                                                                        @staticmethod
                                                                                                        def _build_prompt() -> str:
                                                                                                            return (
                                                                                                                "You are a travel ticket extraction engine.\n"
                                                                                                                "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                "Return ONLY JSON matching the response schema.\n"
                                                                                                                "Rules:\n"
                                                                                                                "1) Use exact field names from schema.\n"
                                                                                                                "2) Do not add unknown keys.\n"
                                                                                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                "4) Keep flights in chronological order.\n"
                                                                                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                            )                                                                                                            @staticmethod
                                                                                                            def _build_prompt() -> str:
                                                                                                                return (
                                                                                                                    "You are a travel ticket extraction engine.\n"
                                                                                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                    "Return ONLY JSON matching the response schema.\n"
                                                                                                                    "Rules:\n"
                                                                                                                    "1) Use exact field names from schema.\n"
                                                                                                                    "2) Do not add unknown keys.\n"
                                                                                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                    "4) Keep flights in chronological order.\n"
                                                                                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                )                                                                                                                @staticmethod
                                                                                                                def _build_prompt() -> str:
                                                                                                                    return (
                                                                                                                        "You are a travel ticket extraction engine.\n"
                                                                                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                        "Return ONLY JSON matching the response schema.\n"
                                                                                                                        "Rules:\n"
                                                                                                                        "1) Use exact field names from schema.\n"
                                                                                                                        "2) Do not add unknown keys.\n"
                                                                                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                        "4) Keep flights in chronological order.\n"
                                                                                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                    )                                                                                                                    @staticmethod
                                                                                                                    def _build_prompt() -> str:
                                                                                                                        return (
                                                                                                                            "You are a travel ticket extraction engine.\n"
                                                                                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                            "Return ONLY JSON matching the response schema.\n"
                                                                                                                            "Rules:\n"
                                                                                                                            "1) Use exact field names from schema.\n"
                                                                                                                            "2) Do not add unknown keys.\n"
                                                                                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                            "4) Keep flights in chronological order.\n"
                                                                                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                        )                                                                                                                        @staticmethod
                                                                                                                        def _build_prompt() -> str:
                                                                                                                            return (
                                                                                                                                "You are a travel ticket extraction engine.\n"
                                                                                                                                "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                "Return ONLY JSON matching the response schema.\n"
                                                                                                                                "Rules:\n"
                                                                                                                                "1) Use exact field names from schema.\n"
                                                                                                                                "2) Do not add unknown keys.\n"
                                                                                                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                "4) Keep flights in chronological order.\n"
                                                                                                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                            )                                                                                                                            @staticmethod
                                                                                                                            def _build_prompt() -> str:
                                                                                                                                return (
                                                                                                                                    "You are a travel ticket extraction engine.\n"
                                                                                                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                    "Return ONLY JSON matching the response schema.\n"
                                                                                                                                    "Rules:\n"
                                                                                                                                    "1) Use exact field names from schema.\n"
                                                                                                                                    "2) Do not add unknown keys.\n"
                                                                                                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                    "4) Keep flights in chronological order.\n"
                                                                                                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                )                                                                                                                                @staticmethod
                                                                                                                                def _build_prompt() -> str:
                                                                                                                                    return (
                                                                                                                                        "You are a travel ticket extraction engine.\n"
                                                                                                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                        "Return ONLY JSON matching the response schema.\n"
                                                                                                                                        "Rules:\n"
                                                                                                                                        "1) Use exact field names from schema.\n"
                                                                                                                                        "2) Do not add unknown keys.\n"
                                                                                                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                        "4) Keep flights in chronological order.\n"
                                                                                                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                    )                                                                                                                                    @staticmethod
                                                                                                                                    def _build_prompt() -> str:
                                                                                                                                        return (
                                                                                                                                            "You are a travel ticket extraction engine.\n"
                                                                                                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                            "Return ONLY JSON matching the response schema.\n"
                                                                                                                                            "Rules:\n"
                                                                                                                                            "1) Use exact field names from schema.\n"
                                                                                                                                            "2) Do not add unknown keys.\n"
                                                                                                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                            "4) Keep flights in chronological order.\n"
                                                                                                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                        )                                                                                                                                        @staticmethod
                                                                                                                                        def _build_prompt() -> str:
                                                                                                                                            return (
                                                                                                                                                "You are a travel ticket extraction engine.\n"
                                                                                                                                                "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                                "Return ONLY JSON matching the response schema.\n"
                                                                                                                                                "Rules:\n"
                                                                                                                                                "1) Use exact field names from schema.\n"
                                                                                                                                                "2) Do not add unknown keys.\n"
                                                                                                                                                "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                                "4) Keep flights in chronological order.\n"
                                                                                                                                                "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                                "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                                "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                                "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                            )                                                                                                                                            @staticmethod
                                                                                                                                            def _build_prompt() -> str:
                                                                                                                                                return (
                                                                                                                                                    "You are a travel ticket extraction engine.\n"
                                                                                                                                                    "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                                    "Return ONLY JSON matching the response schema.\n"
                                                                                                                                                    "Rules:\n"
                                                                                                                                                    "1) Use exact field names from schema.\n"
                                                                                                                                                    "2) Do not add unknown keys.\n"
                                                                                                                                                    "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                                    "4) Keep flights in chronological order.\n"
                                                                                                                                                    "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                                    "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                                    "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                                    "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                                )                                                                                                                                                @staticmethod
                                                                                                                                                def _build_prompt() -> str:
                                                                                                                                                    return (
                                                                                                                                                        "You are a travel ticket extraction engine.\n"
                                                                                                                                                        "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                                        "Return ONLY JSON matching the response schema.\n"
                                                                                                                                                        "Rules:\n"
                                                                                                                                                        "1) Use exact field names from schema.\n"
                                                                                                                                                        "2) Do not add unknown keys.\n"
                                                                                                                                                        "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                                        "4) Keep flights in chronological order.\n"
                                                                                                                                                        "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                                        "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                                        "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                                        "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                                    )                                                                                                                                                    @staticmethod
                                                                                                                                                    def _build_prompt() -> str:
                                                                                                                                                        return (
                                                                                                                                                            "You are a travel ticket extraction engine.\n"
                                                                                                                                                            "Extract itinerary and passenger details from the provided document.\n"
                                                                                                                                                            "Return ONLY JSON matching the response schema.\n"
                                                                                                                                                            "Rules:\n"
                                                                                                                                                            "1) Use exact field names from schema.\n"
                                                                                                                                                            "2) Do not add unknown keys.\n"
                                                                                                                                                            "3) If a value is missing, return an empty string for strings, 0 for counts.\n"
                                                                                                                                                            "4) Keep flights in chronological order.\n"
                                                                                                                                                            "5) Date format: 'DD MMM' (e.g., '23 JUL') when available.\n"
                                                                                                                                                            "6) ai_confidence must be between 0.0 and 1.0.\n"
                                                                                                                                                            "7) Convert all airline carrier names into standard 2-letter IATA airline codes (e.g., TK for Turkish Airlines, SV for Saudia, ET for Ethiopian Airlines).\n"
                                                                                                                                                            "8) Convert all departure and arrival cities/countries into their official 3-letter IATA airport codes (e.g., LOS for Lagos, DOH for Doha, ABV for Abuja, MED for Madinah, JED for Jeddah).\n"
                                                                                                                                                        )
