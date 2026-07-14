import base64
import json
import requests
import streamlit as st

class VisaExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()

    def extract(self, uploaded_file) -> dict:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        # This will write to your log exactly what URL the app is using
        print(f"CRITICAL_DEBUG: The app is using URL: {url}")
        
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{"parts": [{"text": "Extract details"}, {"inline_data": {"mime_type": uploaded_file.type, "data": base64.b64encode(uploaded_file.getvalue()).decode("utf-8")}}]}],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"CRITICAL_DEBUG: API responded with status {response.status_code} and message: {response.text}")
        
        response.raise_for_status()
        
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json\n", "")
        return json.loads(raw_text)
