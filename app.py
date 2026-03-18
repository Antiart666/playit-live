import streamlit as st
import os
import base64
from pathlib import Path

# --- 1. CONFIG & SETUP ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def format_song_name(name):
    """PIPPI_LÅNGSTRUMP -> Pippi Långstrump"""
    return name.replace('_', ' ').strip().title()

def get_library_map():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md")])
    return {format_song_name(f): f for f in files}

def get_base64_bin_file(bin_file):
    if bin_file.exists():
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. THE STAGE-SAFE UI (ANTI-KEYBOARD & TOP-ALIGNED) ---
st.markdown(f"""
    <style>
    /* Grundtema */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    .main .block-container {{
        padding-top: 140px !important; 
        padding-left: 10px !important;
        padding-right: 10px !important;
    }}

    /* FIXED HEADER */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 120px; 
        background-color: #ffffff;
        border-bottom: 1px solid #eeeeee;
        display: flex;
        align-items: flex-start; /* Justerat till överkant */
        justify-content: space-between;
        padding: 10px 15px;
        z-index: 999999;
    }}

    /* LOGOTYP */
    .logo-container {{
        transform: rotate(-8deg);
        flex-shrink: 0;
        margin-top: 5px;
    }}
    
    .logo-img {{
        height: 100px; 
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 30px;
        color: #000000;
        border: 4px solid #000000;
        padding: 5px 15px;
        border-radius: 10px;
    }}

    /* NATIVE SELECT (TANGENTBORDS-SPÄRR) */
    .nav-center {{
        width: 35%; /* Minskad bredd enligt önskemål */
        margin-top: 15px; /* Placerad i överkant */
    }}

    .native-select {{
        width: 100%;
        height: 45px;
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #dddddd;
        border-radius: 12px;
        padding: 0 10px;
        font-size: 16px; /* 16px krävs för att iOS inte ska auto-zooma */
        appearance: none;
        -webkit-appearance: none;
        cursor: pointer;
        outline: none;
    }}

    /* EXIT-KNAPP */
    .exit-container {{
        margin-top: 15px;
    }}

    .exit-link {{
        background-color: #f5f5f5;
        color: #000000 !important;
        padding: 10px 20px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 800;
        font-size: 13px;
        text-transform: uppercase;
        border: 1px solid #dddddd;
    }}

    /* SONG TEXT CONTAINER */
    .song-text-container {{
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important; 
        word-wrap: break-word !important; 
        color: #000000 !important;
        padding-bottom: 70vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & NAVIGATION ---
song_map = get_library_map()
query_params = st.query_params
active_song = query_params.get("song", None)

# --- 4. RENDER HEADER ---
logo_b64 = get_base64_bin_file(LOGO_PATH)
logo_html = f'<div class="logo-fallback">PLAYIT</div>'
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">'

# Bygg HTML-options för native select
options_html = f'<option value="">VÄLJ LÅT...</option>'
for snyggt_namn, filnamn in song_map.items():
    is_selected = "selected" if active_song == filnamn else ""
    options_html += f'<option value="{filnamn}" {is_selected}>{snyggt_namn.upper()}</option>'

# Injicera Header med Native HTML Select (tangentbordssäkert)
st.markdown(f"""
    <div class="stage-header">
        <div class="logo-container">
            <a href="/" target="_self" style="text-decoration:none;">{logo_html}</a>
        </div>
        <div class="nav-center">
            <select class="native-select" onchange="window.location.href='?song=' + encodeURIComponent(this.value)">
                {options_html}
            </select>
        </div>
        <div class="exit-container">
            <a href="/" target="_self" class="exit-link">EXIT</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 5. RENDER CONTENT ---
if active_song and active_song in [v for k, v in song_map.items()]:
    file_path = LIB_DIR / f"{active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            lyrics = f.read()
        st.markdown(f'<div class="song-text-container">{lyrics}</div>', unsafe_allow_html=True)
else:
    st.write("") # Tom startsida

# --- 6. AUTO-SCROLL ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
