import streamlit as st
import os
import base64

# 1. Konfiguration
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Snyggar till filnamn för listvyn."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert."""
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

# --- DESIGN (Logga vänster, Hem-knapp höger, inga extra kontroller) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STANDARD-ELEMENT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXT */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }}

    /* LOGGAN (Vänster, mindre, -8 grader lutning) */
    .nav-logo-left {{
        position: fixed !important;
        top: 25px !important;
        left: 20px !important;
        width: 95px !important;
        height: auto !important;
        z-index: 999999 !important;
        transform: rotate(-8deg) !important;
        filter: drop-shadow(2px 2px 3px rgba(0,0,0,0.1));
        pointer-events: none;
    }}

    /* HEM-KNAPPEN (Höger, snyggad med skugga) */
    div[data-testid="stButton"] > button[key="home_nav_btn"] {{
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        width: 110px !important;
        height: 50px !important;
        z-index: 1000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        color: #000000 !important;
        text-transform: uppercase !important;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.15) !important;
        cursor: pointer !important;
    }}

    /* SPACER FÖR ATT TEXTEN INTE SKA HAMNA UNDER HEADERN */
    .top-spacer {{
        height: 100px;
        display: block;
    }}

    /* LÄSRUTAN (GRÄNSLÖS & TABS-SÄKER) */
    .song-display {{
        height: 92vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        padding: 5px !important;
        border: none !important;
        
        /* Courier för perfekta tabs */
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important; 
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK & STATE ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# RITA LOGGAN (Vänster)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo-left">', unsafe_allow_html=True)
else:
    st.markdown('<div class="nav-logo-left" style="font-weight:900;">LOGO</div>', unsafe_allow_html=True)

# RITA HEM-KNAPPEN (Höger)
if st.button("HEM", key="home_nav_btn"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # ARKIVVYN
        st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, f in enumerate(valid_files):
                    with cols[i % 2]:
                        full_path = os.path.join(root, f)
                        if st.button(clean_title(f), key=full_path):
                            st.session_state.song_path = full_path
                            st.session_state.view = "song"
                            st.rerun()

    else:
        # SCENVYN (Låten)
        st.markdown('<div style="height:70px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Bara texten, inga kontroller
            full_text = content + ("\n" * 65)

            st.markdown(f'<div id="song-view" class="song-display">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
