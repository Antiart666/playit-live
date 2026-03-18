import streamlit as st
import os
import base64
from pathlib import Path

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

# --- 2. THE STAGE-SAFE UI (LIGHT MODE ONLY) ---
st.markdown(f"""
    <style>
    /* Tvinga ljus bakgrund i hela appen */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    /* Göm Streamlits standard-element */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    .main .block-container {{
        padding-top: 100px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER (LJUS) */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 85px;
        background-color: #ffffff;
        border-bottom: 1px solid #eeeeee;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        z-index: 999999;
    }}

    /* LOGOTYP (Stor & Rundad) */
    .logo-link {{
        transform: rotate(-8deg);
        text-decoration: none;
        display: block;
        flex-shrink: 0;
    }}
    
    .logo-img {{
        height: 65px; 
        width: auto;
        border-radius: 12px;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 26px;
        color: #000000;
        background: #ffffff;
        padding: 8px 15px;
        border: 3px solid #000000;
        border-radius: 12px;
    }}

    /* NATIVE SELECT (LJUS & RUNDAD) */
    .nav-center {{
        flex-grow: 1;
        margin: 0 20px;
        max-width: 55%;
    }}

    .native-select {{
        width: 100%;
        height: 50px;
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #eeeeee;
        border-radius: 15px; /* Rundade hörn */
        padding: 0 15px;
        font-size: 16px;
        appearance: none;
        -webkit-appearance: none;
        cursor: pointer;
        outline: none;
    }}

    /* EXIT-KNAPP (LJUSGRÅ/SVART & RUNDAD) */
    .exit-btn {{
        background-color: #f5f5f5;
        color: #000000 !important;
        padding: 12px 20px;
        border-radius: 15px; /* Rundade hörn */
        text-decoration: none;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        border: 1px solid #eeeeee;
        flex-shrink: 0;
    }}
    
    .exit-btn:active {{
        background-color: #eeeeee;
    }}

    /* LÅT-BEHÅLLARE (TABS) */
    .tab-content {{
        font-family: 'Roboto Mono', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 20px;
        line-height: 1.6;
        padding-bottom: 70vh;
        -webkit-overflow-scrolling: touch;
    }}

    .landing-page {{
        text-align: center;
        margin-top: 20vh;
        color: #dddddd;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & NAVIGATION ---
query_params = st.query_params
active_song = query_params.get("song", None)
song_list = get_library()

# --- 4. RENDER HEADER ---
logo_html = '<div class="logo-fallback">PLAYIT</div>'
if LOGO_PATH.exists():
    try:
        base64_logo = get_base64_bin_file(str(LOGO_PATH))
        logo_html = f'<img src="data:image/png;base64,{base64_logo}" class="logo-img">'
    except:
        pass

# HTML-Select
options_html = f'<option value="" {"selected" if not active_song else ""}>VÄLJ LÅT...</option>'
for song in song_list:
    selected_attr = 'selected' if active_song == song else ''
    options_html += f'<option value="{song}" {selected_attr}>{song.upper()}</option>'

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
        st.error("Kunde inte läsa filen.")
else:
    st.markdown("""
        <div class="landing-page">
            <h1 style="font-weight:900; color:#f0f0f0; font-size: 3rem;">PLAYIT LIVE</h1>
            <p style="color:#cccccc;">ANVÄND MENYN OVAN</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. AUTO-SCROLL TO TOP ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
