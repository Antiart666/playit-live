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

# Root och Library-hantering
LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# Whitelist: Skanna /library för .md-filer
def get_library():
    return sorted([f.stem for f in LIB_DIR.glob("*.md")])

def get_base64_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 2. THE STAGE-SAFE UI (CSS) ---
# Vi injicerar CSS för att tvinga fram vit bakgrund, fixera headern och hantera monospace-tabs.
st.markdown(f"""
    <style>
    /* Nollställ Streamlits standard-UI */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    .main .block-container {{
        padding-top: 90px !important;
        padding-left: 15px !important;
        padding-right: 15px !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER */
    .stage-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 75px;
        background-color: #ffffff;
        border-bottom: 3px solid #000000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        z-index: 999999;
    }}

    /* LOGOTYP / HEM-KNAPP */
    .logo-link {{
        transform: rotate(-8deg);
        text-decoration: none;
        display: block;
    }}
    
    .logo-img {{
        height: 50px;
        width: auto;
    }}
    
    .logo-fallback {{
        font-weight: 900;
        font-size: 24px;
        color: #ffffff;
        background: #000000;
        padding: 5px 15px;
        border: 2px solid #000000;
    }}

    /* NATIVE SELECT (ANTI-KEYBOARD) */
    .nav-center {{
        flex-grow: 1;
        margin: 0 20px;
        max-width: 50%;
    }}

    .native-select {{
        width: 100%;
        height: 45px;
        background-color: #1a1a1a;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 0 10px;
        font-size: 16px; /* 16px förhindrar auto-zoom på iOS */
        appearance: none;
        -webkit-appearance: none;
        cursor: pointer;
    }}

    /* EXIT-KNAPP */
    .exit-btn {{
        background-color: #ff0000;
        color: #ffffff !important;
        padding: 12px 20px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 800;
        font-size: 14px;
        text-transform: uppercase;
        border: none;
    }}

    /* LÅT-BEHÅLLARE (TABS) */
    .tab-content {{
        font-family: 'Roboto Mono', 'Courier New', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 18px;
        line-height: 1.5;
        padding-bottom: 60em; /* Motsvarar ca 60 tomma rader */
        -webkit-overflow-scrolling: touch;
    }}

    /* ARKIV-GRID (STARTSIDA) */
    .archive-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }}

    .archive-item {{
        background-color: #ffffff;
        border: 4px solid #000000;
        color: #000000 !important;
        text-align: center;
        padding: 40px 10px;
        text-decoration: none;
        font-weight: 900;
        font-size: 18px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 120px;
    }}

    .archive-item:active {{
        background-color: #000000;
        color: #ffffff !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & NAVIGATION ---
# Hantera URL-parametrar för låtval
params = st.query_params
active_song = params.get("song", None)
song_list = get_library()

# --- 4. RENDER HEADER ---
# Förbered loggan (Base64 för stabil rendering eller text-fallback)
logo_html = '<div class="logo-fallback">PLAYIT</div>'
if LOGO_PATH.exists():
    try:
        base64_logo = get_base64_bin_file(str(LOGO_PATH))
        logo_html = f'<img src="data:image/png;base64,{base64_logo}" class="logo-img">'
    except:
        pass

# Förbered HTML för rullistan
options_html = '<option value="">VALD LÅT...</option>'
for song in song_list:
    selected_attr = 'selected' if active_song == song else ''
    options_html += f'<option value="{song}" {selected_attr}>{song.upper()}</option>'

# Injicera Header
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
    # LÄS-LÄGE (Vyläge 2)
    file_path = LIB_DIR / f"{active_song}.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Säkerställ padding med 60 tomma rader enligt manifestet
        full_content = content + ("\n" * 60)
        
        st.markdown(f'<div class="tab-content">{full_content}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"FEL VID LÄSNING: {e}")
else:
    # STARTSIDA / ARKIV (Vyläge 1)
    st.markdown("<h2 style='color:black; font-weight:900;'>ARKIV</h2>", unsafe_allow_html=True)
    
    if not song_list:
        st.info("Inga .md-filer hittades i /library. Lägg till filer för att börja.")
    else:
        grid_html = '<div class="archive-grid">'
        for song in song_list:
            grid_html += f'<a href="?song={song}" target="_self" class="archive-item">{song}</a>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

# --- 6. AUTO-SCROLL TO TOP SCRIPT ---
# Tvingar skärmen till toppen vid varje låtbyte
st.markdown("""
    <script>
    var mainContainer = window.parent.document.querySelector('.main');
    if (mainContainer) {
        mainContainer.scrollTop = 0;
    }
    </script>
""", unsafe_allow_html=True)
