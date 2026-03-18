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
    # Ersätt understreck med mellanslag och fixa stor/liten bokstav per ord
    return name.replace('_', ' ').strip().title()

def get_library_map():
    """Skapar en mappning mellan snygga namn och filnamn"""
    files = sorted([f.stem for f in LIB_DIR.glob("*.md")])
    return {format_song_name(f): f for f in files}

def get_base64_bin_file(bin_file):
    if bin_file.exists():
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. THE STAGE-SAFE UI (LIGHT & ROUNDED) ---
st.markdown(f"""
    <style>
    /* Grundtema */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    /* Göm menyer */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    .main .block-container {{
        padding-top: 170px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
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
        padding: 0 20px;
        z-index: 999999;
    }}

    /* LOGOTYP (XXL + 20%) */
    .logo-container {{
        transform: rotate(-8deg);
        flex-shrink: 0;
    }}
    
    .logo-img {{
        height: 160px; /* Ännu större */
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 60px;
        color: #000000;
        background: #ffffff;
        padding: 15px 35px;
        border: 6px solid #000000;
        border-radius: 20px;
    }}

    /* STÄNG AV TANGENTBORD PÅ SELECTBOX */
    /* Vi tvingar Streamlits selectbox att bara reagera på klick, inte text-input */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}
    
    /* EXIT-KNAPP */
    .exit-link {{
        background-color: #f5f5f5;
        color: #000000 !important;
        padding: 18px 30px;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 800;
        font-size: 16px;
        text-transform: uppercase;
        border: 1px solid #dddddd;
        flex-shrink: 0;
    }}

    /* LÅT-INNEHÅLL */
    .tab-content {{
        font-family: 'Roboto Mono', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 24px;
        line-height: 1.6;
        padding-bottom: 85vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIK ---
song_map = get_library_map()
snygga_namn = ["VÄLJ LÅT..."] + list(song_map.keys())

# --- 4. RENDER HEADER ---
# Logga
logo_b64 = get_base64_bin_file(LOGO_PATH)
logo_html = f'<div class="logo-fallback">PLAYIT</div>'
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">'

# Vi använder st.columns inuti en fixerad div-struktur för att få Streamlit-widgets att sitta rätt
header_placeholder = st.empty()

with header_placeholder:
    # Vi skapar själva den visuella headern
    st.markdown(f'<div class="stage-header"><div class="logo-container">{logo_html}</div><div id="widget-area" style="width:45%;"></div><a href="/" target="_self" class="exit-link">EXIT</a></div>', unsafe_allow_html=True)

# Placera Streamlits selectbox i mitten (vi döljer labeln)
# Denna widget hamnar nu "ovanpå" headern tack vare CSS-tricks eller positionering
with st.container():
    # Vi använder en kolumn-layout för att centrera widgeten i det tomma hålet i headern
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        # Flytta upp widgeten i headern med CSS
        st.markdown('<div style="position:fixed; top:45px; width:45%; z-index:1000000;">', unsafe_allow_html=True)
        val k = st.selectbox(
            "Select Song",
            options=snygga_namn,
            label_visibility="collapsed",
            key="song_selector"
        )
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. RENDER CONTENT ---
if k != "VÄLJ LÅT...":
    actual_filename = song_map[k]
    file_path = LIB_DIR / f"{actual_filename}.md"
    
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="tab-content">{content}</div>', unsafe_allow_html=True)
else:
    # Startsida helt tom
    st.write("")

# --- 6. AUTO-SCROLL ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
