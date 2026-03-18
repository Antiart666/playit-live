import streamlit as st
import os
from pathlib import Path

# --- KONFIGURATION & SETUP ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Biblioteksinställningar
LIB_DIR = Path("library")
if not LIB_DIR.exists():
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    # Skapa exempel-filer om mappen är tom för demo
    (LIB_DIR / "Exempellåt 1.md").write_text("# Exempellåt 1\nC | G | Am | F", encoding="utf-8")
    (LIB_DIR / "Exempellåt 2.md").write_text("# Exempellåt 2\nD | A | Bm | G", encoding="utf-8")

# Hämta låtlista (sorterad)
song_files = sorted([f.stem for f in LIB_DIR.glob("*.md")])

# --- CSS: FIXERAD HEADER & SCEN-ANPASSAD STYLING ---
st.markdown("""
    <style>
    /* Ta bort Streamlits standard-padding i toppen */
    .block-container { padding-top: 5rem !important; padding-bottom: 20rem !important; }
    
    /* Göm Streamlits standard-menyer för renare scen-vy */
    #MainMenu, footer, header {visibility: hidden;}

    /* FIXERAD HEADER */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: #0e1117;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        border-bottom: 2px solid #333;
    }

    /* LOGGA (Vänster) */
    .header-logo {
        color: #ff4b4b;
        font-weight: 800;
        font-size: 1.2rem;
        text-transform: uppercase;
        margin-top: 5px;
    }

    /* RULLISTA (Mitten) - Undviker Tangentbords-fällan via CSS-styling av HTML Select */
    .custom-select-container {
        flex-grow: 1;
        margin: 0 15px;
        max-width: 500px;
    }

    .custom-select {
        width: 100%;
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #444;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px; /* Förhindrar zoom på iOS */
        appearance: none;
    }

    /* EXIT-KNAPP (Höger) */
    .exit-btn {
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
        font-weight: bold;
        text-decoration: none;
        font-size: 0.9rem;
    }

    /* TAB-RENDERING (Monospace & Scroll) */
    .tab-content {
        font-family: 'Roboto Mono', monospace;
        white-space: pre !important;
        overflow-x: auto;
        background-color: #111;
        padding: 20px;
        border-radius: 8px;
        line-height: 1.5;
        font-size: 1.1rem;
        color: #ddd;
    }

    /* GRID-SYSTEM FÖR STARTSIDA */
    .song-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 15px;
        padding-top: 20px;
    }
    
    .stButton>button {
        width: 100%;
        height: 80px;
        background-color: #262730;
        color: white;
        border: 1px solid #444;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIK: HANTERA VALD LÅT ---
query_params = st.query_params
current_song = query_params.get("song", None)

def set_song():
    # Callback från den dolda widgeten eller URL-parameter
    pass

# --- RENDERERING: HEADER ---
# Vi använder en kombination av HTML för layout och Streamlit query_params för interaktion
cols = st.columns([1, 4, 1])

with st.container():
    st.markdown(f"""
        <div class="fixed-header">
            <div class="header-logo">PLAYIT PRO</div>
            <div class="custom-select-container">
                <form action="/">
                    <select class="custom-select" onchange="window.location.href='?song=' + this.value">
                        <option value="" {"selected" if not current_song else ""}>Välj låt...</option>
                        {''.join([f'<option value="{s}" {"selected" if current_song == s else ""}>{s}</option>' for s in song_files])}
                    </select>
                </form>
            </div>
            <a href="/" target="_self" class="exit-btn">EXIT</a>
        </div>
    """, unsafe_allow_html=True)

# --- RENDERERING: INNEHÅLL ---
if current_song:
    # Låtvy
    file_path = LIB_DIR / f"{current_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        st.markdown(f'<div class="tab-content">{content}</div>', unsafe_allow_html=True)
        
        # Extra padding i botten för att kunna skrolla förbi sista raden
        st.markdown("<div style='height: 60vh;'></div>", unsafe_allow_html=True)
    else:
        st.error("Låten hittades inte.")
        if st.button("Tillbaka till start"):
            st.query_params.clear()
            st.rerun()
else:
    # Startsida (Grid)
    st.subheader("BIBLIOTEK")
    if not song_files:
        st.info("Inga .md-filer hittades i mappen 'library'.")
    else:
        # Skapa ett rutnät med knappar
        cols_per_row = 2 # Anpassat för mobil
        rows = [song_files[i:i + cols_per_row] for i in range(0, len(song_files), cols_per_row)]
        
        for row in rows:
            st_cols = st.columns(cols_per_row)
            for idx, song_name in enumerate(row):
                if st_cols[idx].button(song_name, key=song_name):
                    st.query_params["song"] = song_name
                    st.rerun()
