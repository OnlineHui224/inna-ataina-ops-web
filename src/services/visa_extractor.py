import json
from google import genai
from google.genai import types
from src.core.logger import logger

class VisaExtractor:
    def __init__(self, api_key: str):
        # Your API key will now route through the modern Client architecture
        self.api_key = api_key.strip() if api_key else ""
        if not self.api_key:
            raise ValueError("API key missing")
        
        self.client = genai.Client(api_key=self.api_key)

    def extract(self, uploaded_file) -> dict:
        prompt = (
            "You are a Visa data extractor. Read this travel document/visa. "
            "Extract ONLY: NAME, PASSPORT NUMBER, VISA NUMBER. "
            "Return JSON: {\"NAME\": \"string\", \"PASSPORT NUMBER\": \"string\", \"VISA NUMBER\": \"string\"}"
        )

        try:
            file_bytes = uploaded_file.getvalue()
            
            # The new SDK requires this specific format for reading files
            document_part = types.Part.from_bytes(
                data=file_bytes, 
                mime_type=uploaded_file.type
            )
            
            # Generate the content using the modern configuration
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[prompt, document_part],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                )
            )
            
            raw_text = response.text.strip()
            if "```" in raw_text:
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                
            return json.loads(raw_text)
            
        except Exception as e:
            logger.error(f"Modern SDK Extraction failed: {str(e)}")
            raise ValueError(f"API Request failed: {str(e)}")
