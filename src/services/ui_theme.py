"""
INNA ATAINA OPS PRO — presentation layer.

Styling and HTML helpers only. No business logic lives here, so nothing in this
file can alter an operational workflow.
"""

import base64
import os

# --- SURFACES -----------------------------------------------------------
APP_BG = "#F5F7FA"          # application background, cool grey
SURFACE = "#FFFFFF"         # primary surface
SURFACE_2 = "#F6FAFC"       # information surface, blue-white
BORDER = "#DDE6ED"
BORDER_STRONG = "#C9D6E0"

# --- INK ----------------------------------------------------------------
NAVY = "#0B1B2E"
NAVY_2 = "#122A45"
NAVY_3 = "#1D3A5C"
INK = "#12202F"
MUTED = "#5B7286"
FAINT = "#8A9CAC"

# --- BRAND --------------------------------------------------------------
CYAN = "#1E9BD7"
CYAN_6 = "#1682B8"
CYAN_1 = "#EAF5FB"
CYAN_2 = "#CFE8F6"

OK = "#1C7F5A"
OK_BG = "#E8F5EF"
WARN = "#A96A05"
WARN_BG = "#FBF3E4"
DANGER = "#C03A22"
DANGER_BG = "#FBEDEA"

RADIUS = "12px"
RADIUS_SM = "9px"

# Presentation-only lookup: expands an IATA code to a city label under the code.
# Unknown codes simply render without a city line.
AIRPORTS = {
    "KAN": "Kano", "LOS": "Lagos", "ABV": "Abuja", "PHC": "Port Harcourt",
    "ADD": "Addis Ababa", "JED": "Jeddah", "MED": "Madinah", "RUH": "Riyadh",
    "DMM": "Dammam", "CAI": "Cairo", "IST": "Istanbul", "SAW": "Istanbul",
    "DXB": "Dubai", "AUH": "Abu Dhabi", "SHJ": "Sharjah", "DOH": "Doha",
    "AMM": "Amman", "BEY": "Beirut", "KRT": "Khartoum", "NBO": "Nairobi",
    "ACC": "Accra", "ABJ": "Abidjan", "DKR": "Dakar", "CMN": "Casablanca",
    "TUN": "Tunis", "ALG": "Algiers", "JNB": "Johannesburg", "CPT": "Cape Town",
    "LHR": "London", "LGW": "London", "MAN": "Manchester", "CDG": "Paris",
    "AMS": "Amsterdam", "FRA": "Frankfurt", "MUC": "Munich", "BRU": "Brussels",
    "MAD": "Madrid", "FCO": "Rome", "ATH": "Athens", "JFK": "New York",
    "IAD": "Washington", "ATL": "Atlanta", "YYZ": "Toronto", "KUL": "Kuala Lumpur",
    "SIN": "Singapore", "JKT": "Jakarta", "CGK": "Jakarta", "KHI": "Karachi",
    "LHE": "Lahore", "ISB": "Islamabad", "DAC": "Dhaka", "BOM": "Mumbai",
    "DEL": "Delhi", "COK": "Kochi", "MCT": "Muscat", "BAH": "Bahrain",
    "KWI": "Kuwait", "TAS": "Tashkent", "YNB": "Yanbu", "TIF": "Taif",
}


def inject_theme(st) -> None:
    """Injects the OPS PRO theme. Call once, before any content."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
  font-family:'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing:antialiased;
}}
.stApp {{ background:{APP_BG}; color:{INK}; }}
#MainMenu, footer {{ visibility:hidden; height:0; }}
header[data-testid="stHeader"] {{ background:transparent; height:0; }}
.block-container {{ padding:1.4rem 2rem 5rem; max-width:1240px; }}
h1,h2,h3,h4,h5 {{ color:{NAVY}; letter-spacing:-.015em; }}
p, li, span, label, div {{ text-wrap:pretty; }}
::selection {{ background:{CYAN_2}; }}
:focus-visible {{ outline:2px solid {CYAN}; outline-offset:2px; border-radius:4px; }}

/* ================= HERO ================= */
.ia-hero {{
  position:relative; overflow:hidden; border-radius:{RADIUS};
  background:linear-gradient(135deg,{NAVY} 0%,{NAVY_2} 62%,{NAVY_3} 100%);
  padding:32px 36px; margin:0 0 26px;
  display:flex; align-items:center; gap:26px;
  box-shadow:0 1px 2px rgba(11,27,46,.10), 0 10px 30px rgba(11,27,46,.14);
}}
.ia-hero .motif {{ position:absolute; inset:0; opacity:.5; pointer-events:none; }}
.ia-hero .glow {{ position:absolute; inset:0; pointer-events:none;
  background:radial-gradient(560px 240px at 84% -30%,rgba(30,155,215,.30),transparent 68%); }}
.ia-hero .mark {{ position:relative; width:84px; height:84px; border-radius:50%;
  background:#fff; flex:none; display:grid; place-items:center; overflow:hidden;
  box-shadow:0 4px 18px rgba(0,0,0,.26); }}
.ia-hero .mark img {{ width:100%; height:100%; object-fit:cover; }}
.ia-hero .txt {{ position:relative; min-width:0; }}
.ia-hero .name {{ font-size:31px; font-weight:700; color:#fff; line-height:1.06;
  letter-spacing:-.02em; }}
.ia-hero .prod {{ font-size:16px; font-weight:600; color:{CYAN}; margin-top:6px;
  letter-spacing:-.005em; }}
.ia-hero .meta {{ font-size:11.5px; font-weight:500; color:#8AA2B8; margin-top:9px;
  letter-spacing:.1em; text-transform:uppercase; }}
.ia-hero .right {{ position:relative; margin-left:auto; }}
.ia-status-pill {{ display:inline-flex; align-items:center; gap:9px;
  background:rgba(255,255,255,.10); border-radius:999px; padding:8px 15px;
  font-size:12.5px; font-weight:600; color:#DCE8F2; white-space:nowrap;
  backdrop-filter:blur(6px); }}
.ia-status-pill i {{ width:7px; height:7px; border-radius:50%; background:#37C98D;
  box-shadow:0 0 0 3px rgba(55,201,141,.22); display:block;
  animation:iaPulse 2.6s ease-in-out infinite; }}

/* ================= TABS ================= */
.stTabs [data-baseweb="tab-list"] {{
  gap:4px; background:{SURFACE}; border:1px solid {BORDER}; border-radius:{RADIUS};
  padding:6px; margin-bottom:30px; box-shadow:0 1px 2px rgba(11,27,46,.05);
}}
.stTabs [data-baseweb="tab"] {{
  height:auto; padding:12px 24px; border-radius:{RADIUS_SM}; background:transparent;
  font-size:13.5px; font-weight:600; letter-spacing:.01em; color:{MUTED};
  transition:background .18s, color .18s;
}}
.stTabs [data-baseweb="tab"]:hover {{ background:{SURFACE_2}; color:{NAVY}; }}
.stTabs [aria-selected="true"] {{
  background:{NAVY} !important; color:#fff !important; font-weight:700;
  box-shadow:inset 0 -2px 0 {CYAN}, 0 2px 8px rgba(11,27,46,.18);
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display:none; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:2px; }}

/* ================= TASK INTRO ================= */
.ia-intro {{ margin:0 0 26px; }}
.ia-intro .eyebrow {{ font-size:11px; font-weight:700; letter-spacing:.14em;
  color:{CYAN_6}; text-transform:uppercase; }}
.ia-intro h2 {{ font-size:26px; font-weight:700; margin:9px 0 8px; letter-spacing:-.02em; }}
.ia-intro p {{ margin:0; font-size:14.5px; font-weight:400; color:{MUTED};
  line-height:1.6; max-width:66ch; }}
.ia-intro .tags {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
.ia-intro .tags span {{ font-size:11px; font-weight:600; color:{MUTED};
  background:{SURFACE_2}; border:1px solid {BORDER}; border-radius:999px; padding:5px 11px; }}

/* ================= PANELS ================= */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background:{SURFACE}; border:1px solid {BORDER}; border-radius:{RADIUS} !important;
  padding:22px 24px 20px; box-shadow:0 1px 2px rgba(11,27,46,.05);
}}
.ia-panelhead {{ display:flex; align-items:baseline; gap:10px; margin:0 0 16px; }}
.ia-panelhead .t {{ font-size:15px; font-weight:700; color:{NAVY}; letter-spacing:-.01em; }}
.ia-panelhead .s {{ font-size:12px; font-weight:500; color:{FAINT}; }}
.ia-sublabel {{ font-size:11px; font-weight:700; letter-spacing:.12em; color:{FAINT};
  text-transform:uppercase; margin:18px 0 2px; }}

/* ================= UPLOAD PANEL ================= */
.ia-uphead {{ display:flex; align-items:center; gap:16px; margin-bottom:16px; }}
.ia-uphead .tile {{ width:46px; height:46px; border-radius:{RADIUS_SM}; flex:none;
  background:{CYAN_1}; border:1px solid {CYAN_2}; display:grid; place-items:center; }}
.ia-uphead .t {{ font-size:15px; font-weight:700; color:{NAVY}; }}
.ia-uphead .s {{ font-size:12.5px; font-weight:500; color:{MUTED}; margin-top:3px; }}
.ia-uphead .fmt {{ margin-left:auto; display:flex; gap:6px; }}
.ia-uphead .fmt span {{ font-size:10px; font-weight:700; letter-spacing:.06em;
  color:{MUTED}; background:{SURFACE_2}; border:1px solid {BORDER};
  border-radius:5px; padding:4px 8px; }}

[data-testid="stFileUploader"] section {{
  border:1px dashed {CYAN_2}; background:{SURFACE_2}; border-radius:{RADIUS_SM};
  padding:22px; transition:border-color .18s, background .18s;
}}
[data-testid="stFileUploader"] section:hover {{ border-color:{CYAN}; background:{CYAN_1}; }}
[data-testid="stFileUploader"] section small {{ color:{MUTED}; }}
[data-testid="stFileUploader"] button {{ border-radius:{RADIUS_SM} !important; }}
[data-testid="stFileUploader"] label {{ display:none; }}
[data-testid="stFileUploaderDropzoneInstructions"] div span {{ font-weight:600; }}

.ia-doc {{ display:flex; align-items:center; gap:13px; background:{SURFACE};
  border:1px solid {BORDER}; border-radius:{RADIUS_SM}; padding:11px 14px; margin-top:9px;
  transition:border-color .16s, box-shadow .16s; }}
.ia-doc:hover {{ border-color:{BORDER_STRONG}; box-shadow:0 2px 8px rgba(11,27,46,.06); }}
.ia-doc .ic {{ width:32px; height:32px; border-radius:7px; flex:none; display:grid;
  place-items:center; background:{CYAN_1}; color:{CYAN_6}; font-size:9.5px; font-weight:800; }}
.ia-doc .nm {{ font-size:13.5px; font-weight:600; color:{INK}; overflow:hidden;
  text-overflow:ellipsis; white-space:nowrap; }}
.ia-doc .sz {{ margin-left:auto; font-size:11.5px; font-weight:500; color:{FAINT};
  white-space:nowrap; }}

/* ================= BUTTONS ================= */
.stButton > button, .stDownloadButton > button {{
  border-radius:{RADIUS_SM}; font-family:'Manrope',sans-serif; font-weight:600;
  font-size:14.5px; letter-spacing:-.005em; min-height:46px; padding:.6rem 1.6rem;
  border:1px solid {BORDER}; background:{SURFACE}; color:{NAVY};
  transition:background .18s, border-color .18s, transform .18s, box-shadow .18s;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  background:{SURFACE_2}; border-color:{BORDER_STRONG}; color:{NAVY};
  transform:translateY(-1px); box-shadow:0 4px 14px rgba(11,27,46,.09);
}}
.stButton > button[kind="primary"] {{
  background:{NAVY}; border-color:{NAVY}; color:#fff; font-weight:700;
  box-shadow:0 2px 8px rgba(11,27,46,.20);
}}
.stButton > button[kind="primary"]:hover {{
  background:{NAVY_2}; border-color:{NAVY_2}; box-shadow:0 8px 22px rgba(11,27,46,.26);
}}
.stDownloadButton > button {{
  background:{CYAN}; border-color:{CYAN}; color:#fff; font-weight:700;
  box-shadow:0 2px 8px rgba(30,155,215,.24);
}}
.stDownloadButton > button:hover {{
  background:{CYAN_6}; border-color:{CYAN_6}; color:#fff;
  box-shadow:0 8px 22px rgba(30,155,215,.30);
}}
.stButton > button:active, .stDownloadButton > button:active {{ transform:translateY(0); }}
.stButton > button:disabled {{ opacity:.45; }}

/* ================= FORM CONTROLS ================= */
label, .stTextInput label, .stSelectbox label, .stDateInput label {{
  font-size:13px !important; font-weight:600 !important; color:{NAVY} !important;
  letter-spacing:-.005em; padding-bottom:2px !important;
}}
.stTextInput input, .stDateInput input, .stNumberInput input {{
  border-radius:{RADIUS_SM} !important; border:1px solid {BORDER} !important;
  background:{SURFACE} !important; font-family:'Manrope',sans-serif !important;
  font-size:14px !important; font-weight:500 !important; padding:.62rem .85rem !important;
  color:{INK} !important; transition:border-color .16s, box-shadow .16s;
}}
.stTextInput input::placeholder {{ color:{FAINT}; font-weight:400; }}
.stTextInput input:hover, .stDateInput input:hover {{ border-color:{BORDER_STRONG} !important; }}
.stTextInput input:focus, .stDateInput input:focus {{
  border-color:{CYAN} !important; box-shadow:0 0 0 3px {CYAN_1} !important;
}}
div[data-baseweb="select"] > div {{
  border-radius:{RADIUS_SM} !important; border:1px solid {BORDER} !important;
  background:{SURFACE} !important; min-height:46px; font-family:'Manrope',sans-serif;
  font-size:14px; font-weight:500; transition:border-color .16s, box-shadow .16s;
}}
div[data-baseweb="select"] > div:hover {{ border-color:{BORDER_STRONG} !important; }}
div[data-baseweb="select"] > div:focus-within {{
  border-color:{CYAN} !important; box-shadow:0 0 0 3px {CYAN_1} !important;
}}
div[data-baseweb="select"] svg {{ color:{MUTED}; }}
div[data-baseweb="popover"] li {{ font-family:'Manrope',sans-serif; font-size:13.5px;
  font-weight:500; }}
div[data-baseweb="popover"] li:hover {{ background:{CYAN_1} !important; }}
[data-baseweb="popover"] > div {{ border-radius:{RADIUS_SM} !important;
  box-shadow:0 12px 32px rgba(11,27,46,.16) !important; }}

/* ================= STATUS CARD ================= */
.ia-conn {{ display:flex; align-items:center; gap:15px; background:{SURFACE};
  border:1px solid {BORDER}; border-radius:{RADIUS}; padding:16px 20px;
  box-shadow:0 1px 2px rgba(11,27,46,.05); }}
.ia-conn .tile {{ width:42px; height:42px; border-radius:{RADIUS_SM}; flex:none;
  background:{OK_BG}; display:grid; place-items:center; }}
.ia-conn .l {{ font-size:11px; font-weight:700; letter-spacing:.12em; color:{FAINT};
  text-transform:uppercase; }}
.ia-conn .v {{ font-size:14.5px; font-weight:600; color:{NAVY}; margin-top:3px; }}
.ia-conn .state {{ margin-left:auto; display:inline-flex; align-items:center; gap:8px;
  background:{OK_BG}; border-radius:999px; padding:6px 13px; font-size:12px;
  font-weight:700; color:{OK}; white-space:nowrap; }}
.ia-conn .state i {{ width:7px; height:7px; border-radius:50%; background:{OK}; display:block;
  animation:iaPulse 2.6s ease-in-out infinite; }}

/* ================= NOTES ================= */
.ia-note {{ display:flex; gap:12px; align-items:flex-start; border-radius:{RADIUS_SM};
  padding:14px 17px; font-size:14px; font-weight:500; line-height:1.55; margin:16px 0;
  animation:iaFade .26s ease both; }}
.ia-note b {{ font-weight:700; }}
.ia-note .ic {{ flex:none; margin-top:1px; }}
.ia-note.ok {{ background:{OK_BG}; color:#156044; }}
.ia-note.warn {{ background:{WARN_BG}; color:#7E4F04; }}
.ia-note.bad {{ background:{DANGER_BG}; color:#962C19; }}

/* ================= JOURNEY SUMMARY ================= */
.ia-summary {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:{RADIUS};
  padding:24px 26px; margin-bottom:16px; box-shadow:0 1px 2px rgba(11,27,46,.05);
  animation:iaFade .3s ease both; }}
.ia-summary .lead {{ display:flex; align-items:flex-end; gap:26px; flex-wrap:wrap;
  padding-bottom:20px; border-bottom:1px solid {BORDER}; }}
.ia-summary .lead .who .k {{ font-size:11px; font-weight:700; letter-spacing:.12em;
  color:{FAINT}; text-transform:uppercase; }}
.ia-summary .lead .who .v {{ font-size:25px; font-weight:700; color:{NAVY};
  letter-spacing:-.02em; margin-top:5px; line-height:1.1; }}
.ia-summary .lead .pnr {{ margin-left:auto; text-align:right; }}
.ia-summary .lead .pnr .k {{ font-size:11px; font-weight:700; letter-spacing:.12em;
  color:{FAINT}; text-transform:uppercase; }}
.ia-summary .lead .pnr .v {{ font-family:ui-monospace,'SFMono-Regular',Menlo,monospace;
  font-size:22px; font-weight:700; color:{CYAN_6}; margin-top:5px; letter-spacing:.06em; }}
.ia-summary .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
  gap:22px 30px; padding-top:20px; }}
.ia-summary .grid .k {{ font-size:11px; font-weight:700; letter-spacing:.12em;
  color:{FAINT}; text-transform:uppercase; }}
.ia-summary .grid .v {{ font-size:16px; font-weight:600; color:{INK}; margin-top:6px; }}

/* ================= SEGMENTS ================= */
.ia-seg {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:{RADIUS};
  padding:20px 24px; margin-bottom:12px; box-shadow:0 1px 2px rgba(11,27,46,.05);
  transition:border-color .18s, box-shadow .18s; animation:iaFade .3s ease both; }}
.ia-seg:hover {{ border-color:{CYAN_2}; box-shadow:0 6px 20px rgba(11,27,46,.08); }}
.ia-seg .row {{ display:grid; grid-template-columns:1fr minmax(120px,1.3fr) 1fr;
  gap:20px; align-items:center; }}
.ia-seg .code {{ font-size:25px; font-weight:700; color:{NAVY}; letter-spacing:-.01em;
  line-height:1; }}
.ia-seg .city {{ font-size:12.5px; font-weight:500; color:{MUTED}; margin-top:6px; }}
.ia-seg .time {{ font-size:15px; font-weight:600; color:{INK}; margin-top:8px; }}
.ia-seg .arr {{ text-align:right; }}
.ia-seg .mid {{ display:flex; align-items:center; gap:8px; }}
.ia-seg .line {{ flex:1; height:1px; background:linear-gradient(90deg,{BORDER},{CYAN_2}); }}
.ia-seg .dot {{ width:6px; height:6px; border-radius:50%; background:{CYAN}; flex:none; }}
.ia-seg .plane {{ color:{CYAN}; font-size:15px; line-height:1; flex:none; }}
.ia-seg .foot {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap;
  margin-top:16px; padding-top:14px; border-top:1px solid {BORDER}; }}
.ia-seg .foot .d {{ font-size:12.5px; font-weight:600; color:{MUTED};
  letter-spacing:.04em; text-transform:uppercase; }}
.ia-seg .foot .sep {{ width:3px; height:3px; border-radius:50%; background:{FAINT}; }}
.ia-seg .foot .fn {{ font-size:12.5px; font-weight:700; color:{NAVY_3};
  background:{SURFACE_2}; border:1px solid {BORDER}; border-radius:6px; padding:3px 9px; }}
.ia-seg .foot .idx {{ margin-left:auto; font-size:11px; font-weight:700; color:{FAINT};
  letter-spacing:.1em; text-transform:uppercase; }}

/* ================= TABLE ================= */
.stDataFrame {{ border:1px solid {BORDER}; border-radius:{RADIUS}; overflow:hidden;
  box-shadow:0 1px 2px rgba(11,27,46,.05); }}
.stDataFrame thead tr th {{
  background:{NAVY} !important; color:#fff !important; font-weight:600 !important;
  font-size:11px !important; letter-spacing:.08em; text-transform:uppercase;
  border-color:{NAVY_2} !important;
}}
.stDataFrame tbody tr td {{ font-size:13px !important; }}
.stDataFrame tbody tr:nth-child(even) {{ background:{SURFACE_2}; }}

/* ================= MISC ================= */
.stSpinner > div {{ border-top-color:{CYAN} !important; }}
[data-testid="stExpander"] details {{ border-radius:{RADIUS_SM} !important;
  border-color:{BORDER} !important; background:{SURFACE}; }}
[data-testid="stExpander"] summary {{ font-size:13px; font-weight:600; color:{MUTED}; }}
.stAlert {{ border-radius:{RADIUS_SM}; }}
hr {{ border:0; border-top:1px solid {BORDER}; margin:32px 0; }}

@keyframes iaFade {{ from {{ opacity:0; transform:translateY(7px); }} to {{ opacity:1; transform:none; }} }}
@keyframes iaPulse {{ 0%,100% {{ opacity:.45; }} 50% {{ opacity:1; }} }}

@media (max-width:900px) {{
  .block-container {{ padding:1rem 1.1rem 3rem; }}
  .ia-hero {{ flex-direction:column; align-items:flex-start; gap:18px; padding:26px 22px; }}
  .ia-hero .right {{ margin-left:0; }}
  .ia-hero .name {{ font-size:25px; }}
  .ia-seg .row {{ grid-template-columns:1fr; gap:14px; }}
  .ia-seg .arr {{ text-align:left; }}
  .ia-seg .mid {{ padding:2px 0; }}
  .ia-summary .lead .pnr {{ margin-left:0; text-align:left; }}
  .stTabs [data-baseweb="tab"] {{ padding:11px 14px; font-size:12px; }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def logo_data_uri(path: str) -> str:
    try:
        if path and os.path.exists(path):
            with open(path, "rb") as fh:
                return "data:image/png;base64," + base64.b64encode(fh.read()).decode("utf-8")
    except Exception:
        pass
    return ""


_MOTIF = (
    '<svg class="motif" viewBox="0 0 1200 200" preserveAspectRatio="none" aria-hidden="true">'
    '<path d="M-20 168 C 280 168, 470 44, 780 30 C 980 21, 1120 34, 1240 52" fill="none" '
    'stroke="rgba(30,155,215,.34)" stroke-width="1" stroke-dasharray="5 7"/>'
    '<path d="M-20 190 C 320 190, 520 96, 900 84 C 1050 79, 1160 86, 1240 96" fill="none" '
    'stroke="rgba(255,255,255,.07)" stroke-width="1"/>'
    '<circle cx="780" cy="30" r="2.5" fill="rgba(30,155,215,.6)"/>'
    '<circle cx="470" cy="86" r="2" fill="rgba(255,255,255,.22)"/>'
    '<circle cx="1035" cy="40" r="2" fill="rgba(255,255,255,.18)"/>'
    "</svg>"
)


def hero(st, logo_uri: str, status: str = "System Online") -> None:
    mark = f'<div class="mark"><img src="{logo_uri}" alt="Inna Ataina Travels"></div>' if logo_uri else ""
    st.markdown(
        f"""<div class="ia-hero">{_MOTIF}<div class="glow"></div>{mark}
  <div class="txt">
    <div class="name">INNA ATAINA TRAVELS</div>
    <div class="prod">Operations Automation Pro</div>
    <div class="meta">Internal Operations Workspace</div>
  </div>
  <div class="right"><span class="ia-status-pill"><i></i>{status}</span></div>
</div>""",
        unsafe_allow_html=True,
    )


def task_intro(st, eyebrow: str, title: str, description: str, tags=()) -> None:
    chips = "".join(f"<span>{t}</span>" for t in tags)
    tag_block = f'<div class="tags">{chips}</div>' if chips else ""
    st.markdown(
        f'<div class="ia-intro"><div class="eyebrow">{eyebrow}</div>'
        f"<h2>{title}</h2><p>{description}</p>{tag_block}</div>",
        unsafe_allow_html=True,
    )


def panel_head(st, title: str, subtitle: str = "") -> None:
    sub = f'<span class="s">{subtitle}</span>' if subtitle else ""
    st.markdown(
        f'<div class="ia-panelhead"><span class="t">{title}</span>{sub}</div>',
        unsafe_allow_html=True,
    )


def sublabel(st, text: str) -> None:
    st.markdown(f'<div class="ia-sublabel">{text}</div>', unsafe_allow_html=True)


_DOC_ICON = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1682B8" '
    'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M14 2.5H7a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7.5Z"/>'
    '<path d="M14 2.5v5h5"/><path d="M9 13h6M9 17h4"/></svg>'
)


def upload_head(st, title: str, subtitle: str, formats=("PDF", "JPG", "PNG")) -> None:
    fmt = "".join(f"<span>{f}</span>" for f in formats)
    st.markdown(
        f'<div class="ia-uphead"><div class="tile">{_DOC_ICON}</div>'
        f'<div><div class="t">{title}</div><div class="s">{subtitle}</div></div>'
        f'<div class="fmt">{fmt}</div></div>',
        unsafe_allow_html=True,
    )


def _size(n: int) -> str:
    if n >= 1_048_576:
        return f"{n / 1_048_576:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n} B"


def doc_rows(st, files) -> None:
    rows = "".join(
        f'<div class="ia-doc"><div class="ic">{f.name.rsplit(".", 1)[-1].upper()[:4]}</div>'
        f'<div class="nm">{f.name}</div><div class="sz">{_size(getattr(f, "size", 0) or 0)}</div></div>'
        for f in files
    )
    st.markdown(rows, unsafe_allow_html=True)


_NOTE_ICONS = {
    "ok": '<svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7"/></svg>',
    "warn": '<svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v5"/><path d="M12 17h.01"/><circle cx="12" cy="12" r="9"/></svg>',
    "bad": '<svg class="ic" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="m15 9-6 6M9 9l6 6"/></svg>',
}


def note(st, kind: str, html: str) -> None:
    st.markdown(
        f'<div class="ia-note {kind}">{_NOTE_ICONS.get(kind, "")}<div>{html}</div></div>',
        unsafe_allow_html=True,
    )


def connection_card(st, label: str, value: str, state: str = "Connected") -> None:
    icon = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1C7F5A" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
            '<ellipse cx="12" cy="6" rx="7.5" ry="3"/><path d="M4.5 6v12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V6"/>'
            '<path d="M4.5 12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3"/></svg>')
    st.markdown(
        f'<div class="ia-conn"><div class="tile">{icon}</div>'
        f'<div><div class="l">{label}</div><div class="v">{value}</div></div>'
        f'<div class="state"><i></i>{state}</div></div>',
        unsafe_allow_html=True,
    )


def _plural(n, singular: str, plural_word: str) -> str:
    try:
        n_int = int(n)
    except Exception:
        return f"{n} {plural_word}"
    return f"{n_int} {singular if n_int == 1 else plural_word}"


def journey_summary(st, passenger, pnr, carrier, adults, children, total) -> None:
    travellers = _plural(adults, "Adult", "Adults") + " · " + _plural(children, "Child", "Children")
    total_txt = _plural(total, "passenger", "passengers")
    st.markdown(
        f"""<div class="ia-summary">
  <div class="lead">
    <div class="who"><div class="k">Passenger</div><div class="v">{passenger}</div></div>
    <div class="pnr"><div class="k">Booking reference</div><div class="v">{pnr}</div></div>
  </div>
  <div class="grid">
    <div><div class="k">Carrier</div><div class="v">{carrier}</div></div>
    <div><div class="k">Travellers</div><div class="v">{travellers}</div></div>
    <div><div class="k">Total</div><div class="v">{total_txt}</div></div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def record_summary(st, serial, name, passport, visa_no) -> None:
    st.markdown(
        f"""<div class="ia-summary">
  <div class="lead">
    <div class="who"><div class="k">Traveller</div><div class="v">{name}</div></div>
    <div class="pnr"><div class="k">Serial number</div><div class="v">{serial}</div></div>
  </div>
  <div class="grid">
    <div><div class="k">Passport number</div><div class="v">{passport}</div></div>
    <div><div class="k">Visa number</div><div class="v">{visa_no}</div></div>
  </div>
</div>""",
        unsafe_allow_html=True,
    )


def segment(st, dep, arr, dep_time, arr_time, date, carrier, flight_no, index=None, count=None) -> None:
    dep_city = AIRPORTS.get(str(dep).strip().upper(), "")
    arr_city = AIRPORTS.get(str(arr).strip().upper(), "")
    dep_city_html = f'<div class="city">{dep_city}</div>' if dep_city else ""
    arr_city_html = f'<div class="city">{arr_city}</div>' if arr_city else ""
    idx = f'<span class="idx">Segment {index} of {count}</span>' if index and count else ""
    st.markdown(
        f"""<div class="ia-seg">
  <div class="row">
    <div><div class="code">{dep}</div>{dep_city_html}<div class="time">{dep_time}</div></div>
    <div class="mid"><span class="dot"></span><span class="line"></span>
      <span class="plane">✈</span><span class="line"></span><span class="dot"></span></div>
    <div class="arr"><div class="code">{arr}</div>{arr_city_html}<div class="time">{arr_time}</div></div>
  </div>
  <div class="foot"><span class="d">{date}</span><span class="sep"></span>
    <span class="fn">{carrier} {flight_no}</span>{idx}</div>
</div>""",
        unsafe_allow_html=True,
    )
