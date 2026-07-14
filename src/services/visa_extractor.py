import base64
import json
import requests

class VisaExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()

    def extract(self, uploaded_file) -> dict:
        """Reads a Visa PDF/Image and extracts only the core ID details via REST API."""
        prompt = (
            "You are a Visa data extractor. Read this travel document/visa. "
            "Extract ONLY the following 3 things: \n"
            "1. The passenger's full name.\n"
            "2. The Passport Number.\n"
            "3. The Visa Number.\n"
            "Return EXACTLY this JSON format and nothing else: "
            "{\"NAME\": \"string\", \"PASSPORT NUMBER\": \"string\", \"VISA NUMBER\": \"string\"}"
        )

        file_bytes = uploaded_file.getvalue()
        b64_data = base64.b64encode(file_bytes).decode("utf-8")
        
        payload = {
            "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": uploaded_file.type, "data": b64_data}}]}],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
        }

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json\n", "")
            
        return json.loads(raw_text)
