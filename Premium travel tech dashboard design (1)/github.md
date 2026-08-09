repo: OnlineHui224/inna-ataina-ops-web
branch: main

## Last sync
date: 2026-08-09T22:12:00Z

### Updated in this project
- Premium navy/cyan UI implemented in place in `src/services/web_app.py`; all backend calls preserved.
- Added `src/services/ui_theme.py` — presentation only, no business logic.
- Search-first hotel pickers for the real 3,367-row hotels.xlsx; Madinah manual-entry bug fixed.
- API key removed from `config/settings.json`; `requests` added to requirements (was missing at runtime).

## Screen map
| Project screen | Repo files |
| --- | --- |
| Shell / sidebar / header | src/services/web_app.py, src/services/ui_theme.py |
| Dashboard | src/services/web_app.py |
| Flight Document Ops | src/services/web_app.py, src/services/gemini_extractor.py, src/services/docx_generator.py, src/models/data_schemas.py |
| Visa & Contract Logger | src/services/web_app.py, src/services/visa_extractor.py, src/services/excel_logger.py |
| Hotel Directory | src/services/web_app.py, assets/hotels.xlsx |
| Recent Activity | src/services/web_app.py, visa_data.csv |
| System Status | src/services/web_app.py, docs/STORAGE_STATUS.md |
| OPS PRO.dc.html | visual reference only — not part of the running application |

## Notes
- hotels.xlsx columns: Hotel Name (English), Hotel Name (Arabic), City, License Number, Classification, Status, Hotel ID — 3,367 rows.
- Visa records persist to a local CSV; Google Sheets remains a tracked follow-up (docs/STORAGE_STATUS.md).
- Service modules use absolute `src.` imports, so the app must be launched from the repository root.
