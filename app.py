import streamlit as st
import os
import base64
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def get_library():
    return sorted([f.stem for f in LIB_DIR.glob("*.md")])

def get_base64_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 2. STAGE-SAFE UI (LIGHT MODE) ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    .main .block-container {{
        padding-top: 150px !important; /* Mer plats för XXL-loggan */
        padding-left: 20px !important;
        padding-right: 20px !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 130px; /* Höjd för XXL-logo */
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        z-index: 999999;
    }}

    /* LOGOTYP (YTTERLIGARE 20% STÖRRE) */
    .logo-link {{
        transform: rotate(-8deg);
        text-decoration: none;
        display: block;
        flex-shrink: 0;
    }}
    
    .logo-img {{
        height: 135px; /* Uppskalad ytterligare */
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 52px; /* Gigantisk fallback-text */
        color: #000000;
        background: #ffffff;
        padding: 10px 30px;
        border: 5px solid #000000;
        border-radius: 15px;
    }}

    /* NATIVE SELECT (FÖR ENKEL NAVIGATION) */
    .nav-center {{
        flex-grow: 1;
        margin: 0 15px;
        max-width: 45%;
    }}

    .native-select {{
        width: 100%;
        height: 60px;
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #dddddd;
        border-radius: 20px;
        padding: 0 15px;
        font-size: 20px;
        appearance: none;
        -webkit-appearance: none;
        outline: none;
    }}

    /* EXIT-KNAPP */
    .exit-btn {{
        background-color: #eeeeee;
        color: #000000 !important;
        padding: 15px 25px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 800;
        font-size: 14px;
        text-transform: uppercase;
        border: 1px solid #cccccc;
        flex-shrink: 0;
    }}

    /* LÅT-INNEHÅLL */
    .tab-content {{
        font-family: 'Roboto Mono', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 22px;
        line-height: 1.6;
        padding-bottom: 85vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & PARAMS ---
song_list = get_library()
# Hämta parameter manuellt för maximal säkerhet
query_params = st.query_params
active_song = query_params.get("song", None)

# --- 4. RENDER HEADER ---
logo_html = '<div class="logo-fallback">PLAYIT</div>'
if LOGO_PATH.exists():
    try:
        base64_logo = get_base64_bin_file(str(LOGO_PATH))
        logo_html = f'<img src="data:image/png;base64,{base64_logo}" class="logo-img">'
    except:
        pass

# Bygg options
options_html = f'<option value="">VÄLJ LÅT...</option>'
for song in song_list:
    sel = 'selected' if active_song == song else ''
    options_html += f'<option value="{song}" {sel}>{song.upper()}</option>'

# JAVASCRIPT-NAVIGATION (Tvingar omladdning vid klick)
st.markdown(f"""
    <div class="stage-header">
        <a href="/" target="_self" class="logo-link">
            {logo_html}
        </a>
        <div class="nav-center">
            <select class="native-select" id="songSelect">
                {options_html}
            </select>
        </div>
        <a href="/" target="_self" class="exit-btn">EXIT</a>
    </div>

    <script>
    var select = window.parent.document.getElementById("songSelect");
    if (!select) {{
        // Om vi kör i iframe (standard Streamlit) måste vi leta i parent
        select = document.getElementById("songSelect");
    }}
    
    select.addEventListener('change', function() {{
        var val = encodeURIComponent(this.value);
        if (val) {{
            window.parent.location.assign(window.parent.location.origin + window.parent.location.pathname + "?song=" + val);
        }} else {{
            window.parent.location.assign(window.parent.location.origin + window.parent.location.pathname);
        }}
    }});
    </script>
""", unsafe_allow_html=True)

# --- 5. RENDER CONTENT ---
if active_song and active_song in song_list:
    file_path = LIB_DIR / f"{active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="tab-content">{content}</div>', unsafe_allow_html=True)
else:
    # Startsida helt tom
    st.write("")

# --- 6. CLEANUP SCRIPT ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
