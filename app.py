import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Maximerad yta för scenen
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER ---

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

# --- DESIGN (Logga vänster, Knapp höger, Spikraka tabs) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono:wght@400;700&display=swap');

    /* DÖLJ STANDARD-ELEMENT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXT */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* LOGGAN (Vänster, nu endast 85px bred) */
    .nav-logo-left-final {{
        position: fixed !important;
        top: 25px !important;
        left: 15px !important;
        width: 85px !important;
        height: auto !important;
        z-index: 999999 !important;
        transform: rotate(-8deg) !important;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
        pointer-events: none;
    }}

    /* KNAPPEN "LÅTAR" (Höger, snyggad och tydlig) */
    div[data-testid="stButton"] > button[key="btn_goto_list"] {{
        position: fixed !important;
        top: 20px !important;
        right: 15px !important;
        width: 120px !important;
        height: 55px !important;
        z-index: 1000000 !important;
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        color: #000000 !important;
        text-transform: uppercase !important;
        box-shadow: 4px 4px 12px rgba(0,0,0,0.2) !important;
        cursor: pointer !important;
    }}

    /* SPACER FÖR ATT TEXTEN INTE SKA HAMNA UNDER HEADERN */
    .top-content-spacer {{
        height: 110px;
        display: block;
    }}

    /* LÄSRUTAN (SPIKRAKA TABS) */
    .song-stage-area {{
        height: 92vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        padding: 5px !important;
        border: none !important;
        
        /* Monospace-font tvingar alla tecken att vara lika breda */
        font-family: 'Roboto Mono', 'Courier New', monospace !important;
        font-size: 13px !important; /* Något mindre för att rymma hela tab-rader */
        line-height: 1.1 !important;
        
        /* Förhindrar radbrytning - rader förblir spikraka */
        white-space: pre !important; 
        overflow-x: auto !important;
    }}

    /* ARKIV-KNAPPAR I LISTAN */
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
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo-left-final">', unsafe_allow_html=True)
else:
    st.markdown('<div class="nav-logo-left-final" style="font-weight:900;">LOGO</div>', unsafe_allow_html=True)

# RITA KNAPPEN "LÅTAR" (Höger)
if st.button("LÅTAR", key="btn_goto_list"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas på GitHub.")
else:
    if st.session_state.view == "list":
        # --- ARKIVVYN ---
        st.markdown('<div class="top-content-spacer"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Alla Låtar"
            
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
        # --- SCENVYN (Låten) ---
        st.markdown('<div style="height:75px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Lägger till extra tomrum i slutet så man kan scrolla sista raden till toppen
            full_text = content + ("\n" * 60)

            st.markdown(f'<div id="song-view" class="song-stage-area">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
