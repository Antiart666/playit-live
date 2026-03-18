import streamlit as st
import os
from pathlib import Path

# --- 1. GRUNDLÄGGANDE KONFIGURATION ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Filhantering: Mappen 'library' krävs
LIB_DIR = Path("library")
if not LIB_DIR.exists():
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    # Skapa demo-filer om tomt
    (LIB_DIR / "Exempellåt 1.md").write_text("# LÅT 1\nC      G\nDu är min vän", encoding="utf-8")

# Hämta och sortera låtlista
song_files = sorted([f.stem for f in LIB_DIR.glob("*.md")])

# --- 2. UI & CSS (DESIGN-REGLER) ---
st.markdown(f"""
    <style>
    /* Grundfärg: Vit bakgrund, Svart text */
    .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    /* Ta bort Streamlits standardmarginaler */
    .block-container {{
        padding-top: 80px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }}
    
    #MainMenu, footer, header {{visibility: hidden;}}

    /* FIXED HEADER */
    .fixed-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: #ffffff;
        border-bottom: 2px solid #eeeeee;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        z-index: 99999;
    }}

    /* LOGOTYP (Lutad & Klickbar) */
    .logo-box {{
        transform: rotate(-8deg);
        background-color: #000000;
        color: #ffffff;
        padding: 5px 10px;
        font-weight: 900;
        font-size: 14px;
        text-decoration: none;
        cursor: pointer;
        border-radius: 3px;
    }}

    /* NATIVE SELECT (Inget tangentbord) */
    .nav-select-container {{
        flex-grow: 1;
        margin: 0 10px;
        max-width: 60%;
    }}

    .native-select {{
        width: 100%;
        height: 40px;
        background-color: #333333;
        color: #ffffff;
        border-radius: 8px;
        padding: 5px;
        font-size: 16px; /* Förhindrar auto-zoom i iOS */
        border: none;
    }}

    /* EXIT KNAPP */
    .exit-link {{
        background-color: #ff4b4b;
        color: white !important;
        padding: 8px 12px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        font-size: 12px;
        text-transform: uppercase;
    }}

    /* TEXT-RENDERING (Tabs & Ackord) */
    .tab-area {{
        font-family: 'Roboto Mono', 'Courier New', monospace !important;
        white-space: pre !important;
        overflow-x: auto !important;
        color: #000000 !important;
        background-color: #ffffff;
        font-size: 18px;
        line-height: 1.4;
        padding-bottom: 80vh; /* Gigantiskt tomrum i botten */
    }}

    /* GRID FÖR STARTSIDA */
    .song-grid-button {{
        display: block;
        width: 100%;
        padding: 25px 10px;
        background-color: #f0f2f6;
        border: 2px solid #000000;
        color: #000000;
        text-align: center;
        text-decoration: none;
        font-weight: bold;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 18px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIK & NAVIGATION ---
params = st.query_params
selected_song = params.get("song", None)

# --- 4. RENDERERING: HEADER ---
# Vi injicerar headern som HTML. Native select skickar användaren vidare via URL.
select_options = "".join([
    f'<option value="{s}" {"selected" if selected_song == s else ""}>{s}</option>' 
    for s in song_files
])

st.markdown(f"""
    <div class="fixed-header">
        <a href="/" target="_self" class="logo-box">PLAYIT</a>
        <div class="nav-select-container">
            <select class="native-select" onchange="window.location.href='?song=' + this.value">
                <option value="" disabled { 'selected' if not selected_song else '' }>Välj låt...</option>
                {select_options}
            </select>
        </div>
        <a href="/" target="_self" class="exit-link">EXIT</a>
    </div>
""", unsafe_allow_html=True)

# --- 5. HUVUDVYER ---
if selected_song:
    # LÅTVY
    file_path = LIB_DIR / f"{selected_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Rendera markdown i en div med monospace och overflow-skydd
        st.markdown(f'<div class="tab-area">{content}</div>', unsafe_allow_html=True)
    else:
        st.error("Filen saknas.")
        if st.button("Gå tillbaka"):
            st.query_params.clear()
            st.rerun()
else:
    # ARKIVVY (GRID)
    st.write("### ARKIV")
    if not song_files:
        st.info("Lägg till .md-filer i mappen 'library' för att komma igång.")
    else:
        # Skapa ett 2-kolumns rutnät för stora knappar
        cols = st.columns(2)
        for i, song in enumerate(song_files):
            with cols[i % 2]:
                # Använder HTML-länkar stylade som knappar för snabbhet och stabilitet
                st.markdown(f'<a href="?song={song}" target="_self" class="song-grid-button">{song}</a>', unsafe_allow_html=True)

# --- 6. CLEANUP ---
# Döljer Streamlits footer-padding som ibland dyker upp
st.markdown("<style>div[data-testid='stVerticalBlock'] > div:empty {display:none;}</style>", unsafe_allow_html=True)
