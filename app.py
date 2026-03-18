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
    /* Grundtema - Tvinga vit bakgrund */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    /* Göm Streamlits egna element */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* Huvudcontainer - Flytta ner innehåll under den massiva headern */
    .main .block-container {{
        padding-top: 220px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
    }}

    /* FIXED HEADER */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 190px; 
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 25px;
        z-index: 999999;
    }}

    /* LOGOTYP (Ytterligare 20% större än förra) */
    .logo-container {{
        transform: rotate(-8deg);
        flex-shrink: 0;
    }}
    
    .logo-img {{
        height: 190px; /* XXL storlek */
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 70px;
        color: #000000;
        background: #ffffff;
        padding: 15px 40px;
        border: 8px solid #000000;
        border-radius: 25px;
    }}

    /* STÄNG AV TANGENTBORD PÅ SELECTBOX */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}
    
    /* EXIT-KNAPP */
    .exit-link {{
        background-color: #f8f8f8;
        color: #000000 !important;
        padding: 20px 35px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 800;
        font-size: 18px;
        text-transform: uppercase;
        border: 2px solid #eeeeee;
        flex-shrink: 0;
    }}

    /* LÅT-INNEHÅLL (MONOSPACE) */
    .tab-content {{
        font-family: 'Roboto Mono', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 24px;
        line-height: 1.7;
        padding-bottom: 85vh;
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

# Skapa den fasta bakgrunden för headern
st.markdown(f"""
    <div class="stage-header">
        <div class="logo-container">{logo_html}</div>
        <div style="width:40%;"></div> <a href="/" target="_self" class="exit-link">EXIT</a>
    </div>
""", unsafe_allow_html=True)

# Placera Streamlits selectbox exakt i mitten av headern
cols = st.columns([1, 2, 1])
with cols[1]:
    st.markdown('<div style="position:fixed; top:65px; width:45%; z-index:1000000;">', unsafe_allow_html=True)
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
        st.markdown(f'<div class="tab-content">{lyrics}</div>', unsafe_allow_html=True)
else:
    # Startsida helt ren
    st.write("")

# --- 6. AUTO-SCROLL TO TOP ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
