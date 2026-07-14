import base64
import json
import requests

class VisaExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""
def extract(self, uploaded_file) -> dict:
        print("DEBUG_CHECK: I AM RUNNING THE NEW FILE") # Add this line
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        )

        file_bytes = uploaded_file.getvalue()
        b64_data = base64.b64encode(file_bytes).decode("utf-8")
        
        # Exact payload structure from your working Flight tab
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt}, 
                    {"inline_data": {"mime_type": uploaded_file.type, "data": b64_data}}
                ]
            }],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
        }

        # The URL you confirmed is working
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # Headers identical to your working Flight tab
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        # If this fails, we will see the real error immediately
        response.raise_for_status()
        
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json\n", "")
            
        return json.loads(raw_text)
