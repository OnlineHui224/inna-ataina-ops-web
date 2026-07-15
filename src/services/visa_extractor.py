import base64
import requests
import json
from src.core.logger import logger

class VisaExtractor:
    def __init__(self, api_key: str):
        # 1. HARDCODE TEST: Paste your exact AQ. key inside the quotes below!
        self.api_key = "AQ.PASTE_YOUR_EXACT_KEY_HERE"
        
        if not self.api_key:
            raise ValueError("API key missing")

    def extract(self, uploaded_file) -> dict:
        prompt = (
            "You are a Visa data extractor. Read this travel document/visa. "
            "Extract ONLY: NAME, PASSPORT NUMBER, VISA NUMBER. "
            "Return JSON: {\"NAME\": \"string\", \"PASSPORT NUMBER\": \"string\", \"VISA NUMBER\": \"string\"}"
        )

        file_bytes = uploaded_file.getvalue()
        b64_data = base64.b64encode(file_bytes).decode("utf-8")
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": uploaded_file.type, "data": b64_data}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.0, 
                "responseMimeType": "application/json"
            }
        }

        # 2. FIXED URL: Using 1.5-flash and injecting your API key directly
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        # 3. FIXED HEADERS: Removed the x-goog-api-key to stop the 401 OAuth error
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"API Error {response.status_code}: {response.text}")
            raise ValueError(f"API Request failed: {response.text}")
            
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
        if "```" in raw_text:
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw_text)
