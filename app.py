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

# Initiera session state för låtval om det inte finns
if "active_song_file" not in st.session_state:
    st.session_state.active_song_file = None

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def format_song_name(name):
    """PIPPI_LÅNGSTRUMP -> Pippi Långstrump"""
    return name.replace('_', ' ').strip().title()

def get_library_map():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md")])
    # Skapa en dictionary: { "Snyggt Namn": "filnamn" }
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
        padding-top: 130px !important; 
        padding-left: 10px !important;
        padding-right: 10px !important;
    }}

    /* FIXED HEADER */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 110px; 
        background-color: #ffffff;
        border-bottom: 1px solid #eeeeee;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 5px 15px;
        z-index: 999999;
    }}

    /* LOGOTYP */
    .logo-container {{
        transform: rotate(-8deg);
        flex-shrink: 0;
        margin-top: 5px;
        cursor: pointer;
    }}
    
    .logo-img {{
        height: 90px; 
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 28px;
        color: #000000;
        border: 4px solid #000000;
        padding: 5px 12px;
        border-radius: 10px;
    }}

    /* TANGENTBORDS-SPÄRR FÖR SELECTBOX */
    /* Detta döljer markören och gör fältet oklickbart för textinmatning */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}
    
    /* Justera bredden på Streamlits selectbox-container */
    .stSelectbox {{
        width: 35% !important;
        position: fixed !important;
        top: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 1000000 !important;
    }}

    /* EXIT-KNAPP */
    .exit-btn-fixed {{
        position: fixed;
        top: 15px;
        right: 15px;
        z-index: 1000000;
    }}

    /* SONG TEXT CONTAINER */
    .song-text-container {{
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important; 
        word-wrap: break-word !important; 
        color: #000000 !important;
        padding-top: 20px;
        padding-bottom: 75vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
song_map = get_library_map()
# Vänd på mappen för att kunna slå upp snyggt namn från filnamn
inv_song_map = {v: k for k, v in song_map.items()}

# Hitta index för nuvarande låt i rullistan
options = ["VÄLJ LÅT..."] + list(song_map.keys())
current_index = 0
if st.session_state.active_song_file in inv_song_map:
    current_index = options.index(inv_song_map[st.session_state.active_song_file])

# --- 4. RENDER HEADER (VISUALS ONLY) ---
logo_b64 = get_base64_bin_file(LOGO_PATH)
logo_html = f'<div class="logo-fallback">PLAYIT</div>'
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">'

st.markdown(f"""
    <div class="stage-header">
        <div class="logo-container">{logo_html}</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. FUNCTIONAL WIDGETS ---
# Exit-knapp (använder Streamlit-knapp för stabilitet men stylad som länk)
with st.container():
    col_exit = st.columns([1, 1, 1])
    with col_exit[2]:
        st.markdown('<div class="exit-btn-fixed">', unsafe_allow_html=True)
        if st.button("EXIT", key="exit_btn"):
            st.session_state.active_song_file = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Rullistan (Centrerad och fixerad via CSS)
    with col_exit[1]:
        selected_display_name = st.selectbox(
            "Song Select",
            options=options,
            index=current_index,
            label_visibility="collapsed",
            key="main_selector"
        )
        
        # Uppdatera state om användaren väljer en låt
        if selected_display_name != "VÄLJ LÅT...":
            new_file = song_map[selected_display_name]
            if st.session_state.active_song_file != new_file:
                st.session_state.active_song_file = new_file
                st.rerun()
        else:
            if st.session_state.active_song_file is not None:
                st.session_state.active_song_file = None
                st.rerun()

# --- 6. RENDER CONTENT ---
if st.session_state.active_song_file:
    file_path = LIB_DIR / f"{st.session_state.active_song_file}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            lyrics = f.read()
        
        # 60 tomma rader
        full_lyrics = lyrics + ("\n" * 60)
        st.markdown(f'<div class="song-text-container">{full_lyrics}</div>', unsafe_allow_html=True)
else:
    st.write("") # Ren startsida

# --- 7. AUTO-SCROLL ---
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) { mainContainer.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
