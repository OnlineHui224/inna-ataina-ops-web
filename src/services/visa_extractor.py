import json
import google.generativeai as genai
from src.core.logger import logger

class VisaExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""
        if not self.api_key:
            raise ValueError("API key missing")
        
        # 1. The SDK handles ALL authentication, headers, and OAuth routing automatically
        genai.configure(api_key=self.api_key)

    def extract(self, uploaded_file) -> dict:
        prompt = (
            "You are a Visa data extractor. Read this travel document/visa. "
            "Extract ONLY: NAME, PASSPORT NUMBER, VISA NUMBER. "
            "Return JSON: {\"NAME\": \"string\", \"PASSPORT NUMBER\": \"string\", \"VISA NUMBER\": \"string\"}"
        )

        try:
            # 2. Initialize the correct, stable model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 3. Let the SDK handle the file bytes natively (no manual base64 needed)
            file_bytes = uploaded_file.getvalue()
            
            # 4. Call the API using the official SDK method
            response = model.generate_content(
                [prompt, {"mime_type": uploaded_file.type, "data": file_bytes}],
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
            
            # 5. Parse the result safely
            raw_text = response.text.strip()
            if "```" in raw_text:
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                
            return json.loads(raw_text)
            
        except Exception as e:
            logger.error(f"SDK Extraction failed: {str(e)}")
            raise ValueError(f"API Request failed via SDK: {str(e)}")
