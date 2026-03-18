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

# State-hantering för att undvika URL-strul
if "current_song" not in st.session_state:
    st.session_state.current_song = "VÄLJ LÅT..."

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def format_name(n):
    return n.replace('_', ' ').strip().title()

def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md")])
    return {format_name(f): f for f in files}

def get_logo():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. DEN "HÅRDA" STYLINGEN (CSS) ---
st.markdown(f"""
    <style>
    /* 1. Tvinga vit scen-bakgrund */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    /* 2. Göm ALLT Streamlit-skräp */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer, [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* 3. Den fasta headern i toppen */
    .nav-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100px;
        background: #ffffff;
        border-bottom: 1px solid #eeeeee;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 15px;
    }}

    /* 4. LOGGAN (Vänster) */
    .logo-box {{
        position: absolute;
        left: 15px;
        top: 10px;
        transform: rotate(-8deg);
    }}
    .logo-img {{ height: 80px; width: auto; }}
    .logo-text {{ 
        font-weight: 900; font-size: 24px; border: 3px solid #000; 
        padding: 5px 10px; border-radius: 10px; 
    }}

    /* 5. RULLISTEN (Center + 35% bredd + INGET TANGENTBORD) */
    /* Vi positionerar Streamlits widget exakt över vår nav-bar */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 35% !important;
        z-index: 1000001 !important;
    }}
    
    /* ELIMINERA TANGENTBORD: Gör input-fältet osynligt för klick men behåll containern */
    div[data-baseweb="select"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    /* 6. EXIT-KNAPPEN (Uppe till höger) */
    .stButton > button {{
        position: fixed !important;
        top: 25px !important;
        right: 15px !important;
        width: auto !important;
        background-color: #f5f5f5 !important;
        color: #000000 !important;
        border-radius: 15px !important;
        border: 1px solid #ddd !important;
        font-weight: 800 !important;
        z-index: 1000001 !important;
        padding: 10px 20px !important;
    }}

    /* 7. TEXT-CONTAINER (Din specifikation) */
    .song-display {{
        margin-top: 120px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        color: #000000 !important;
        padding-bottom: 80vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

# Rita Headern (Visuellt för loggan)
logo_b64 = get_logo()
logo_content = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">' if logo_b64 else '<span class="logo-text">PLAYIT</span>'

st.markdown(f"""
    <div class="nav-bar">
        <div class="logo-box">{logo_content}</div>
    </div>
""", unsafe_allow_html=True)

# Ladda låtlista
song_map = get_songs()
options = ["VÄLJ LÅT..."] + list(song_map.keys())

# Placera EXIT-knappen högst upp till höger
if st.button("EXIT"):
    st.session_state.current_song = "VÄLJ LÅT..."
    st.rerun()

# Placera Rullistan i mitten (35% bredd)
selected = st.selectbox(
    "Välj låt",
    options=options,
    index=options.index(st.session_state.current_song) if st.session_state.current_song in options else 0,
    label_visibility="collapsed"
)

# Vid ändring av låt
if selected != st.session_state.current_song:
    st.session_state.current_song = selected
    st.rerun()

# --- 4. VISA INNEHÅLL ---
if st.session_state.current_song != "VÄLJ LÅT...":
    file_name = song_map[st.session_state.current_song]
    path = LIB_DIR / f"{file_name}.md"
    
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Rendera med din specifikation
        st.markdown(f'<div class="song-display">{content}\n' + ('\n' * 60) + '</div>', unsafe_allow_html=True)
else:
    # Startsida helt tom
    st.empty()

# Scroll-fix
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
