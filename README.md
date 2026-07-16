# OPS PRO - API TROUBLESHOOTING LOG

## THE BUG
Error: `401 UNAUTHENTICATED` / `ACCESS_TOKEN_TYPE_UNSUPPORTED`
Cause: Google API servers temporarily rejecting new `AQ.` keys via the `google-genai` Python SDK or when daily limits are exhausted.

## THE FIX
Do NOT upgrade to the new SDK. Do NOT hardcode the key.
The original `requests.post` architecture is the only stable workaround.

1. Endpoint MUST be: 
   url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
   (Note: gemini-1.5-flash will throw a 404 NOT_FOUND error)

2. Headers MUST be configured exactly like this:
   headers = {
       "x-goog-api-key": self.api_key,
       "Content-Type": "application/json"
   }

3. No URL injection needed. Let Streamlit read the key from secrets normally.
