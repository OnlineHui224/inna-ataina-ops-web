"""
INNA ATAINA OPS PRO — presentation layer.

Styling and small HTML helpers only. No business logic lives here, so nothing in
this file can alter an operational workflow.
"""

import base64
import os

NAVY = "#0B1626"
NAVY_2 = "#12233A"
NAVY_3 = "#1C3350"
CYAN = "#1E9BD7"
CYAN_6 = "#1682B8"
CYAN_1 = "#E8F4FB"
STEEL = "#6B7C8F"
LINE = "#DDE3E9"
BG = "#F4F6F8"
OK = "#1C7F5A"
WARN = "#B06A00"
DANGER = "#C8321A"


def inject_theme(st) -> None:
    """Injects the premium navy/cyan theme. Call once, near the top of the app."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{ font-family:'Archivo', system-ui, sans-serif; }}
.stApp {{ background:{BG}; color:{NAVY}; }}
#MainMenu, footer {{ visibility:hidden; height:0; }}
header[data-testid="stHeader"] {{ background:transparent; height:0; }}
.block-container {{ padding:1.2rem 3rem 5rem; max-width:1240px; }}
h1,h2,h3,h4,h5 {{ letter-spacing:-.02em; font-weight:800; color:{NAVY}; }}
hr {{ border:0; border-top:2px solid rgba(11,22,38,.18); margin:1.6rem 0; }}
::selection {{ background:{CYAN_1}; }}

/* ---------------- HERO HEADER ---------------- */
.ia-hero {{
  background:linear-gradient(112deg,{NAVY} 0%,{NAVY_2} 55%,{NAVY_3} 100%);
  padding:30px 36px; margin:0 0 26px; position:relative; overflow:hidden;
  display:flex; align-items:center; gap:22px;
}}
.ia-hero:after {{
  content:""; position:absolute; inset:0; pointer-events:none;
  background:radial-gradient(680px 280px at 92% -40%,rgba(30,155,215,.42),transparent 70%);
}}
.ia-hero img {{ width:62px; height:62px; border-radius:50%; background:#fff;
  object-fit:cover; flex:none; position:relative; box-shadow:0 6px 20px rgba(0,0,0,.28); }}
.ia-hero .txt {{ position:relative; min-width:0; }}
.ia-hero .name {{ font-size:26px; font-weight:800; color:#fff; letter-spacing:-.02em; line-height:1.1; }}
.ia-hero .sub {{ font-size:14px; color:{CYAN}; font-weight:700; margin-top:3px; }}
.ia-hero .tag {{ font-size:10.5px; letter-spacing:.2em; color:#8FA6BC; font-weight:600; margin-top:7px; }}
.ia-hero .right {{ margin-left:auto; position:relative; text-align:right; }}
.ia-hero .chip {{ display:inline-flex; align-items:center; gap:8px; border:1px solid rgba(255,255,255,.22);
  background:rgba(255,255,255,.07); padding:8px 13px; font-size:11.5px; font-weight:700;
  color:#DCE7F1; white-space:nowrap; }}
.ia-hero .chip i {{ width:7px; height:7px; background:{OK}; display:block; font-style:normal;
  animation:iaPulse 2.4s ease-in-out infinite; }}

/* ---------------- TABS ---------------- */
.stTabs [data-baseweb="tab-list"] {{
  gap:0; background:#fff; border:1px solid {LINE}; padding:5px; margin-bottom:22px;
}}
.stTabs [data-baseweb="tab"] {{
  height:auto; padding:13px 26px; border-radius:0; background:transparent;
  font-size:13.5px; font-weight:700; letter-spacing:.03em; color:{STEEL};
  transition:background .16s, color .16s;
}}
.stTabs [data-baseweb="tab"]:hover {{ background:#EEF2F6; color:{NAVY}; }}
.stTabs [aria-selected="true"] {{
  background:{NAVY} !important; color:#fff !important; font-weight:800;
  box-shadow:inset 0 -3px 0 {CYAN};
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display:none; }}

/* ---------------- SECTIONS / CARDS ---------------- */
.ia-sec {{ display:flex; align-items:baseline; gap:12px; margin:6px 0 0; }}
.ia-sec .n {{ font-size:11px; font-weight:800; color:{CYAN_6}; letter-spacing:.14em; }}
.ia-sec .t {{ font-size:19px; font-weight:800; letter-spacing:-.02em; }}
.ia-rule {{ border:0; border-top:2px solid rgba(11,22,38,.18); margin:9px 0 18px; }}
.ia-card {{ background:#fff; border:1px solid {LINE}; padding:22px 24px; margin-bottom:18px; }}
.ia-card.accent {{ border-top:3px solid {CYAN}; }}
.ia-cardhead {{ font-size:9.5px; letter-spacing:.16em; color:{STEEL}; font-weight:700;
  margin-bottom:14px; text-transform:uppercase; }}

/* Native bordered containers used for form groups */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background:#fff; border:1px solid {LINE}; border-top:3px solid {CYAN};
  border-radius:0 !important; padding:6px 20px 14px;
}}

/* ---------------- STATUS BADGE ---------------- */
.ia-status {{ display:inline-flex; align-items:center; gap:11px; background:#fff;
  border:1px solid {LINE}; border-left:3px solid {OK}; padding:11px 16px; }}
.ia-status .d {{ width:7px; height:7px; background:{OK}; display:block; flex:none;
  animation:iaPulse 2.4s ease-in-out infinite; }}
.ia-status .l {{ font-size:9.5px; letter-spacing:.15em; color:{STEEL}; font-weight:700; }}
.ia-status .v {{ font-size:13px; font-weight:800; color:{NAVY}; margin-top:2px; }}

/* ---------------- NOTES ---------------- */
.ia-note {{ background:#fff; border:1px solid {LINE}; padding:14px 18px; font-size:13px;
  line-height:1.6; color:{NAVY_3}; margin:4px 0 14px; animation:iaFade .26s ease both; }}
.ia-note.ok {{ border-left:3px solid {OK}; }}
.ia-note.warn {{ border-left:3px solid {WARN}; }}
.ia-note.bad {{ border-left:3px solid {DANGER}; }}
.ia-note b {{ font-weight:800; color:{NAVY}; }}

/* ---------------- FACT STRIP ---------------- */
.ia-facts {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:1px;
  background:{LINE}; border:1px solid {LINE}; margin:0 0 20px; animation:iaFade .3s ease both; }}
.ia-fact {{ background:#fff; padding:15px 17px; }}
.ia-fact .k {{ font-size:9.5px; letter-spacing:.14em; color:{STEEL}; font-weight:700; }}
.ia-fact .v {{ font-size:17px; font-weight:800; margin-top:5px; word-break:break-word; }}

/* ---------------- FLIGHT LEG ---------------- */
.ia-leg {{ display:grid; grid-template-columns:84px 1fr 84px; gap:18px; align-items:center;
  background:#fff; border:1px solid {LINE}; padding:15px 20px; margin-bottom:9px;
  transition:box-shadow .18s, transform .18s; animation:iaFade .3s ease both; }}
.ia-leg:hover {{ box-shadow:0 8px 22px rgba(11,22,38,.10); transform:translateY(-1px); }}
.ia-leg .code {{ font-size:23px; font-weight:800; letter-spacing:-.02em; line-height:1; }}
.ia-leg .time {{ font-size:12px; color:{STEEL}; font-weight:700; margin-top:5px; }}
.ia-leg .mid {{ text-align:center; }}
.ia-leg .date {{ font-size:10.5px; color:{STEEL}; font-weight:700; letter-spacing:.12em; }}
.ia-leg .track {{ position:relative; height:2px; background:{LINE}; margin:10px 0; }}
.ia-leg .track:before {{ content:""; position:absolute; left:0; top:-2px; width:6px; height:6px;
  background:{CYAN}; }}
.ia-leg .track:after {{ content:"✈"; position:absolute; right:-4px; top:-12px; font-size:15px;
  color:{CYAN}; background:#fff; padding:0 5px; }}
.ia-leg .fno {{ font-size:12.5px; font-weight:800; color:{NAVY_3}; }}

/* ---------------- FILE CHIPS ---------------- */
.ia-files {{ display:flex; flex-wrap:wrap; gap:9px; margin:2px 0 16px; }}
.ia-chip {{ display:inline-flex; align-items:center; gap:9px; background:#fff;
  border:1px solid {LINE}; padding:8px 13px; font-size:12.5px; font-weight:700; }}
.ia-chip .x {{ background:{CYAN_1}; color:{CYAN_6}; font-size:9px; font-weight:800;
  padding:3px 6px; letter-spacing:.06em; }}

/* ---------------- FORM CONTROLS ---------------- */
label, .stTextInput label, .stSelectbox label, .stDateInput label, .stFileUploader label {{
  font-size:11.5px !important; font-weight:700 !important; color:{NAVY} !important;
  letter-spacing:.03em;
}}
.stTextInput input, .stDateInput input, .stNumberInput input {{
  border-radius:0 !important; border:1px solid {LINE} !important; background:#fff !important;
  font-family:'Archivo',sans-serif !important; font-size:13.5px !important; padding:.55rem .7rem !important;
  transition:border-color .15s, box-shadow .15s;
}}
.stTextInput input:focus, .stDateInput input:focus, .stNumberInput input:focus {{
  border-color:{CYAN} !important; box-shadow:0 0 0 3px {CYAN_1} !important;
}}
div[data-baseweb="select"] > div {{
  border-radius:0 !important; border:1px solid {LINE} !important; background:#fff !important;
  font-family:'Archivo',sans-serif; font-size:13.5px; min-height:42px;
  transition:border-color .15s, box-shadow .15s;
}}
div[data-baseweb="select"] > div:hover {{ border-color:{STEEL} !important; }}
div[data-baseweb="select"] > div:focus-within {{
  border-color:{CYAN} !important; box-shadow:0 0 0 3px {CYAN_1} !important;
}}
div[data-baseweb="popover"] li {{ font-family:'Archivo',sans-serif; font-size:13px; }}
div[data-baseweb="popover"] li:hover {{ background:{CYAN_1} !important; }}

/* ---------------- BUTTONS ---------------- */
.stButton > button, .stDownloadButton > button {{
  border-radius:0; font-family:'Archivo',sans-serif; font-weight:800; font-size:13px;
  letter-spacing:.02em; border:1px solid {LINE}; background:#fff; color:{NAVY};
  padding:.6rem 1.25rem; transition:background .16s, border-color .16s, transform .16s, box-shadow .16s;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  background:#EEF2F6; border-color:{STEEL}; color:{NAVY}; transform:translateY(-1px);
}}
.stButton > button[kind="primary"], .stDownloadButton > button {{
  background:{CYAN}; border-color:{CYAN}; color:#fff;
}}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {{
  background:{CYAN_6}; border-color:{CYAN_6}; color:#fff;
  box-shadow:0 10px 24px rgba(30,155,215,.28);
}}
.stButton > button:active, .stDownloadButton > button:active {{ transform:translateY(0); }}
:focus-visible {{ outline:2px solid {CYAN}; outline-offset:2px; }}

/* ---------------- UPLOAD ZONE ---------------- */
[data-testid="stFileUploader"] section {{
  border:2px dashed {CYAN}55; background:linear-gradient(180deg,{CYAN_1},#fff);
  border-radius:0; padding:26px; transition:border-color .18s, box-shadow .18s;
}}
[data-testid="stFileUploader"] section:hover {{
  border-color:{CYAN}; box-shadow:0 0 0 4px rgba(30,155,215,.10);
}}
[data-testid="stFileUploader"] section small {{ color:{STEEL}; }}
[data-testid="stFileUploader"] button {{ border-radius:0 !important; }}

/* ---------------- TABLE ---------------- */
.stDataFrame, [data-testid="stTable"] {{ border:1px solid {LINE}; }}
.stDataFrame thead tr th {{
  background:{NAVY} !important; color:#fff !important; font-weight:700 !important;
  font-size:11px !important; letter-spacing:.08em; text-transform:uppercase;
}}

/* ---------------- MISC ---------------- */
.stSpinner > div {{ border-top-color:{CYAN} !important; }}
[data-testid="stExpander"] details {{ border-radius:0 !important; border-color:{LINE} !important;
  background:#fff; }}
.stAlert {{ border-radius:0; }}

@keyframes iaFade {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:none; }} }}
@keyframes iaPulse {{ 0%,100% {{ opacity:.35; }} 50% {{ opacity:1; }} }}

@media (max-width: 900px) {{
  .block-container {{ padding:1rem 1.2rem 3rem; }}
  .ia-hero {{ flex-direction:column; align-items:flex-start; gap:14px; padding:24px; }}
  .ia-hero .right {{ margin-left:0; text-align:left; }}
  .ia-leg {{ grid-template-columns:1fr; text-align:left; gap:10px; }}
  .stTabs [data-baseweb="tab"] {{ padding:11px 14px; font-size:12px; }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def logo_data_uri(path: str) -> str:
    """Data URI for the brand mark, or '' when the asset is absent."""
    try:
        if path and os.path.exists(path):
            with open(path, "rb") as fh:
                return "data:image/png;base64," + base64.b64encode(fh.read()).decode("utf-8")
    except Exception:
        pass
    return ""


def hero(st, logo_uri: str) -> None:
    img = f'<img src="{logo_uri}" alt="Inna Ataina Travels">' if logo_uri else ""
    st.markdown(
        f"""<div class="ia-hero">{img}
  <div class="txt">
    <div class="name">INNA ATAINA TRAVELS</div>
    <div class="sub">Operations Automation Pro</div>
    <div class="tag">INTERNAL OPERATIONS WORKSPACE</div>
  </div>
  <div class="right"><span class="chip"><i></i>OPS PRO ONLINE</span></div>
</div>""",
        unsafe_allow_html=True,
    )


def section(st, number: str, title: str) -> None:
    num = f'<span class="n">{number}</span>' if number else ""
    st.markdown(
        f'<div class="ia-sec">{num}<span class="t">{title}</span></div><hr class="ia-rule">',
        unsafe_allow_html=True,
    )


def status_badge(st, label: str, value: str) -> None:
    st.markdown(
        f'<div class="ia-status"><span class="d"></span><div>'
        f'<div class="l">{label}</div><div class="v">{value}</div></div></div>',
        unsafe_allow_html=True,
    )


def note(st, kind: str, html: str) -> None:
    st.markdown(f'<div class="ia-note {kind}">{html}</div>', unsafe_allow_html=True)


def facts(st, pairs) -> None:
    cells = "".join(
        f'<div class="ia-fact"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in pairs
    )
    st.markdown(f'<div class="ia-facts">{cells}</div>', unsafe_allow_html=True)


def file_chips(st, files) -> None:
    chips = "".join(
        f'<span class="ia-chip"><span class="x">{f.name.rsplit(".", 1)[-1].upper()}</span>{f.name}</span>'
        for f in files
    )
    st.markdown(f'<div class="ia-files">{chips}</div>', unsafe_allow_html=True)


def flight_leg(st, dep, arr, dep_time, arr_time, date, carrier, flight_no) -> None:
    st.markdown(
        f"""<div class="ia-leg">
  <div><div class="code">{dep}</div><div class="time">{dep_time}</div></div>
  <div class="mid"><div class="date">{date}</div><div class="track"></div>
    <div class="fno">{carrier} · {flight_no}</div></div>
  <div style="text-align:right"><div class="code">{arr}</div><div class="time">{arr_time}</div></div>
</div>""",
        unsafe_allow_html=True,
    )


def group_label(st, title: str) -> None:
    """Small uppercase heading for a bordered st.container group."""
    st.markdown(f'<div class="ia-cardhead">{title}</div>', unsafe_allow_html=True)
