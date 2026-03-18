# --- FULLSTÄNDIG KOD FÖR APP.PY ---
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

# --- FUNKTIONER ---

def clean_title(filename):
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

# --- CSS (Absolut positionering och Tabs-fix) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STANDARD-SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXTSTIL */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* LOGGAN (Spikad till VÄNSTER) */
    .fixed-logo-left {{
        position: fixed !important;
        top: 20px !important;
        left: 15px !important;
        width: 80px !important; /* Mindre som begärt */
        height: auto !important;
        z-index: 1000001 !important;
        transform: rotate(-8deg) !important;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
        pointer-events: none;
    }}

    /* KNAPPEN LÅTAR (Spikad till HÖGER) */
    .fixed-nav-right {{
        position: fixed !important;
        top: 20px !important;
        right: 15px !important;
        z-index: 1000002 !important;
    }}

    .fixed-nav-right button {{
        width: 120px !important;
        height: 50px !important;
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        font-size: 15px !important;
        color: #000000 !important;
        text-transform: uppercase !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15) !important;
        cursor: pointer !important;
    }}

    /* MELLANRUM SÅ ATT TEXTEN INTE HAMNAR BAKOM KNAPPARNA */
    .header-clearance {{
        height: 100px;
        display: block;
    }}

    /* LÄSRUTAN (TABS-SÄKRAD OCH GRÄNSLÖS) */
    .song-reader-final {{
        height: 92vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        padding: 10px 5px !important;
        border: none !important;
        
        /* Monospace fixar så tabs ligger i linje */
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 13px !important; 
        line-height: 1.2 !important;
        
        /* Denna rad stoppar "skeva" tabs genom att aldrig radbryta */
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

# --- 2. LOGIK & NAVIGATION ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# RITA LOGGAN
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="fixed-logo-left">', unsafe_allow_html=True)

# RITA KNAPPEN LÅTAR (I sin fasta position till höger)
st.markdown('<div class="fixed-nav-right">', unsafe_allow_html=True)
if st.button("LÅTAR", key="btn_goto_list"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # ARKIVVYN
        st.markdown('<div class="header-clearance"></div>', unsafe_allow_html=True)
        
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
        st.markdown('<div style="height:75px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Ger lite extra plats i slutet
            full_text = content + ("\n" * 60)

            st.markdown(f'<div id="song-view" class="song-reader-final">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
