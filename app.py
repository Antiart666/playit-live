import streamlit as st
import os
from pathlib import Path

# --- 1. CONFIG & INITIALIZATION ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Säkerställ att biblioteket finns
LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)

# Whitelist-validering av filer
def get_song_list():
    return sorted([f.stem for f in LIB_DIR.glob("*.md")])

def is_valid_song(song_name):
    return (LIB_DIR / f"{song_name}.md").exists()

song_list = get_song_list()

# --- 2. CSS: STAGE-SAFE DESIGN & UI ---
st.markdown(f"""
    <style>
    /* Strikt vit bakgrund och svart text för att tvinga bort Dark Mode-kaos */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    /* Ta bort Streamlits standard-padding och menyer */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}
    
    .block-container {{
        padding-top: 80px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER */
    .fixed-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: #ffffff;
        border-bottom: 2px solid #000000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        z-index: 999999;
    }}

    /* LOGOTYP (HEM-KNAPP) */
    .logo-link {{
        text-decoration: none;
        transform: rotate(-8deg);
        display: inline-block;
    }}
    
    .logo-img {{
        height: 45px;
        width: auto;
        /* Fallback om logo.png saknas */
        font-weight: 900;
        color: #000000;
        border: 3px solid #000000;
        padding: 2px 8px;
    }}

    /* NATIVE SELECT (INGET TANGENTBORD) */
    .nav-center {{
        flex-grow: 1;
        margin: 0 15px;
        max-width: 50%;
    }}

    .native-select {{
        width: 100%;
        height: 45px;
        background-color: #222222; /* Mörk bakgrund för kontrast i headern */
        color: #ffffff;
        border-radius: 5px;
        border: none;
        padding: 0 10px;
        font-size: 16px; /* Viktigt: 16px+ förhindrar auto-zoom på iOS */
        appearance: none;
        -webkit-appearance: none;
    }}

    /* EXIT-KNAPP */
    .exit-btn {{
        background-color: #ff0000;
        color: #ffffff !important;
        padding: 10px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
    }}

    /* LÅTVY: TABS & TEXT */
    .tab-container {{
        font-family: 'Roboto Mono', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        font-size: 18px;
        line-height: 1.4;
        padding-top: 10px;
        padding-bottom: 80vh; /* Möjliggör fri skrollning i botten */
    }}

    /* ARKIV-GRID */
    .grid-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }}

    .grid-item {{
        background-color: #ffffff;
        border: 3px solid #000000;
        color: #000000 !important;
        text-align: center;
        padding: 30px 10px;
        text-decoration: none;
        font-weight: 900;
        font-size: 18px;
        text-transform: uppercase;
        border-radius: 0px;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100px;
    }}

    .grid-item:active {{
        background-color: #000000;
        color: #ffffff !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIK & NAVIGATION ---
# Hämta nuvarande låt från URL
query_params = st.query_params
selected_song = query_params.get("song", None)

# --- 4. RENDERERING: HEADER ---
# Förbered rullistan
options_html = '<option value="">VALD LÅT...</option>'
for song in song_list:
    is_selected = "selected" if selected_song == song else ""
    options_html += f'<option value="{song}" {is_selected}>{song.upper()}</option>'

# Kolla om loggan finns, annars använd text
logo_html = '<div class="logo-img">PLAYIT</div>'
if os.path.exists("logo.png"):
    logo_html = '<img src="app/static/logo.png" class="logo-img">'

st.markdown(f"""
    <div class="fixed-header">
        <a href="/" target="_self" class="logo-link">
            {logo_html}
        </a>
        <div class="nav-center">
            <select class="native-select" onchange="window.location.href='?song=' + this.value">
                {options_html}
            </select>
        </div>
        <a href="/" target="_self" class="exit-btn">EXIT</a>
    </div>
""", unsafe_allow_html=True)

# --- 5. RENDERERING: HUVUDVYER ---

if selected_song and is_valid_song(selected_song):
    # --- LÄS-LÄGE ---
    file_path = LIB_DIR / f"{selected_song}.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Lägg till de 60 tomma raderna i botten
        content_with_padding = content + ("\n" * 60)
        
        st.markdown(f'<div class="tab-container">{content_with_padding}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Fel vid inläsning av fil: {e}")
else:
    # --- ARKIV-LÄGE (GRID) ---
    st.markdown("<h1 style='color:black; margin-top:10px;'>ARKIV</h1>", unsafe_allow_html=True)
    
    if not song_list:
        st.info("Inga låtar hittades i mappen /library. Lägg till .md-filer för att börja.")
    else:
        grid_html = '<div class="grid-container">'
        for song in song_list:
            grid_html += f'<a href="?song={song}" target="_self" class="grid-item">{song}</a>'
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

# --- 6. CLEANUP & NAVIGATION SCRIPT ---
# Script för att säkerställa att vi scrollar till toppen vid ny låt
st.markdown("""
    <script>
    var body = window.parent.document.querySelector(".main");
    if (body) { body.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)
