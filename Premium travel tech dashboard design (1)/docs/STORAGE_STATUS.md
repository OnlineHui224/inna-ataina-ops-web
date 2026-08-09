# Storage status — visa records

**Current behaviour:** `ExcelLogger.log_visa()` writes to `visa_data.csv` in the
application's working directory. It accepts a `sheet_url` argument and does not use it.
The previous UI displayed "Securely connected to Master Live Google Sheet", which did not
match what the code does. That message has been removed; the UI now reports local storage.

**Risk:** on Streamlit Community Cloud the working directory is ephemeral. Records can be
lost on restart or redeploy. Take a manual copy of `visa_data.csv` regularly until this is
resolved.

**No data was changed.** The persistence path itself is untouched — only the wording around
it, so the saved records and serial numbering continue exactly as before.

## To enable real Google Sheets persistence

Needs credentials that are not in the repository:

1. Create a Google Cloud service account and enable the Google Sheets API.
2. Share the target spreadsheet with the service-account email as an Editor.
3. Add the JSON credential to Streamlit secrets as `gcp_service_account`.
4. Add `gspread` and `google-auth` to `requirements.txt`.
5. Extend `ExcelLogger.log_visa()` to append the row to the sheet, keeping the local CSV
   as a fallback so a network failure never loses a record.

Serial-number generation must continue to read the existing rows before assigning a number,
otherwise duplicates will occur.

## Related fixes applied

- **Madinah manual entry** compared the selection against `"Other (Manual Sheet)"` while the
  option was `"Other (Manual Entry)"`, so the manual text field never appeared and the literal
  string was logged. Corrected.
- **API key** removed from `config/settings.json`. The application already prefers
  `st.secrets` / environment variables via `_get_gemini_api_key()`.
  **The removed key must be rotated in Google Cloud** — it remains in git history.
- **requirements.txt** was missing `pandas`, `openpyxl`, `python-docx` and `requests`, all of
  which the application imports at runtime. Added. `google-generativeai` was listed but never
  imported (the extractors call the REST API directly) and has been removed.
