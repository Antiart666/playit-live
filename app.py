import streamlit as st
import os
import base64
from pathlib import Path
from urllib.parse import quote

# --- 1. CORE CONFIGURATION ---
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

# --- 2. THE STAGE-SAFE UI (LJUS DESIGN + MAXI-LOGO) ---
st.markdown(f"""
    <style>
    /* Grundinställningar */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    .main .block-container {{
        padding-top: 130px !important; /* Ökad för att ge plats åt större header */
        padding-left: 20px !important;
        padding-right: 20px !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER (HÖGRE FÖR ATT RYMMA LOGGAN) */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 110px; /* Ökad höjd */
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        z-index: 999999;
    }}

    /* LOGOTYP (70% STÖRRE) */
    .logo-link {{
        transform: rotate(-8deg);
        text-decoration: none;
        display: block;
        flex-shrink: 0;
        margin-left: 10px;
    }}
    
    .logo-img {{
        height: 110px; /* Tidigare ~65px, nu +70% ≈ 110px */
        width: auto;
        border-radius: 15px;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 42px; /* Skalat upp texten också */
        color: #000000;
        background: #ffffff;
        padding: 10px 25px;
        border: 4px solid #000000;
        border-radius: 15px;
    }}

    /* NATIVE SELECT (LJUS & RUNDAD) */
    .nav-center {{
        flex-grow: 1;
        margin: 0 20px;
        max-width: 50%;
    }}

    .native-select {{
        width: 100%;
        height: 55px;
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #eeeeee;
        border-radius: 18px;
        padding: 0 15px;
        font-size: 18px;
        appearance: none;
        -webkit-appearance: none;
        cursor: pointer;
        outline: none;
    }}

    /* EXIT-KNAPP */
    .exit-btn {{
        background-color: #f8f8f8;
        color: #000000 !important;
        padding: 14px 22px;
        border-radius: 18px;
        text-decoration: none;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        border: 1px solid #eeeeee;
        flex-shrink: 0;
    }}

    /* TAB-CONTENT */
    .tab-content {{
        font-family: 'Roboto Mono', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 22px; /* Något större för bättre läsbarhet */
        line-height: 1.6;
        padding-bottom: 85vh;
        -webkit-overflow-scrolling: touch;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & NAVIGATION ---
song_list = get_library()
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

options_html = f'<option value="" {"selected" if not active_song else ""}>VÄLJ LÅT...</option>'
for song in song_list:
    is_selected = "selected" if active_song == song else ""
    options_html += f'<option value="{song}" {is_selected}>{song.upper()}</option>'

st.markdown(f"""
    <div class="stage-header">
        <a href="/" target="_self" class="logo-link">
            {logo_html}
        </a>
        <div class="nav-center">
            <select class="native-select" onchange="window.location.href='?song=' + encodeURIComponent(this.value)">
                {options_html}
            </select>
        </div>
        <a href="/" target="_self" class="exit-btn">EXIT</a>
    </div>
""", unsafe_allow_html=True)

# --- 5. RENDER CONTENT ---
if active_song and active_song in song_list:
    file_path = LIB_DIR / f"{active_song}.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="tab-content">{content}</div>', unsafe_allow_html=True)
    except Exception:
        st.error("Filfel.")
else:
    # Helt tom startsida
    st.write("")

# --- 6. AUTO-SCROLL TO TOP ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
