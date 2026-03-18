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
    """Omvandlar PIPPI_LÅNGSTRUMP till Pippi Långstrump"""
    return name.replace('_', ' ').strip().title()

def get_library_map():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md")])
    return {format_song_name(f): f for f in files}

def get_base64_bin_file(bin_file):
    if bin_file.exists():
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. THE STAGE-SAFE UI (MOBILE OPTIMIZED) ---
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
        padding-top: 170px !important; 
        padding-left: 10px !important;
        padding-right: 10px !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 150px; 
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        z-index: 999999;
    }}

    /* LOGOTYP */
    .logo-container {{
        transform: rotate(-8deg);
        flex-shrink: 0;
        width: 25%;
    }}
    
    .logo-img {{
        height: 120px; 
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 35px;
        color: #000000;
        background: #ffffff;
        padding: 8px 18px;
        border: 4px solid #000000;
        border-radius: 12px;
    }}

    /* TULLLISTAN (SELECTBOX) */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}

    /* EXIT-KNAPP */
    .exit-container {{
        width: 25%;
        display: flex;
        justify-content: flex-end;
    }}

    .exit-link {{
        background-color: #f8f8f8;
        color: #000000 !important;
        padding: 10px 18px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 800;
        font-size: 13px;
        text-transform: uppercase;
        border: 1px solid #eeeeee;
    }}

    /* --- MOBILE OPTIMIZED TEXT CONTAINER --- */
    .song-text-container {{
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important; /* Standardstorlek för mobil läsbarhet */
        line-height: 1.2 !important;
        
        /* VIKTIGT: PRE-WRAP istället för PRE */
        /* Detta bryter rader vid skärmkant men behåller mellanslag */
        white-space: pre-wrap !important; 
        word-wrap: break-word !important; 
        
        color: #000000 !important;
        background-color: #ffffff !important;
        padding: 15px 5px !important;
        tab-size: 4 !important;
        display: block;
        width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIK ---
song_map = get_library_map()
snygga_options = ["VÄLJ LÅT..."] + list(song_map.keys())

# --- 4. RENDER HEADER ---
logo_b64 = get_base64_bin_file(LOGO_PATH)
logo_html = f'<div class="logo-fallback">PLAYIT</div>'
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">'

st.markdown(f"""
    <div class="stage-header">
        <div class="logo-container">{logo_html}</div>
        <div style="width: 45%;"></div>
        <div class="exit-container">
            <a href="/" target="_self" class="exit-link">EXIT</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Selectbox placering
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    st.markdown('<div style="position:fixed; top:50px; width:45%; z-index:1000000;">', unsafe_allow_html=True)
    valda_laten = st.selectbox(
        "Välj låt",
        options=snygga_options,
        label_visibility="collapsed",
        key="stage_select"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. RENDER CONTENT ---
if valda_laten != "VÄLJ LÅT...":
    actual_file = song_map[valda_laten]
    file_path = LIB_DIR / f"{actual_file}.md"
    
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            lyrics = f.read()
        
        # 60 tomma rader för skrollmån
        full_lyrics = lyrics + ("\n" * 60)
        
        st.markdown(f'<div class="song-text-container">{full_lyrics}</div>', unsafe_allow_html=True)
else:
    st.write("")

# --- 6. AUTO-SCROLL ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
