import streamlit as st
import os

# --- 1. SETUP ---
st.set_page_config(page_title="PlayIt! v3.2", layout="wide", initial_sidebar_state="expanded")

# Hitta rätt mapp oavsett om vi är på datorn eller i molnet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(BASE_DIR, "library")

# Skapa mappen om den inte finns (så appen inte kraschar)
if not os.path.exists(LIB_PATH):
    os.makedirs(LIB_PATH)

# --- 2. CSS (Mobiloptimerad) ---
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stApp { background-color: #1a1a1a; color: #e0e0e0; }
    .song-title { color: #ffffff; font-weight: 800; font-size: 1.8rem; margin-bottom: 10px; }
    .song-sheet { 
        background-color: #111111; 
        padding: 1.5rem; 
        border-radius: 15px; 
        border: 1px solid #333;
        font-family: 'Consolas', monospace !important;
        white-space: pre !important;
        font-size: 1.1rem;
        line-height: 1.4;
    }
    .song-sheet b, .song-sheet strong { color: #38bdf8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTION FÖR ATT HITTA LÅTAR ---
def get_songs():
    # Listar alla .md-filer i library-mappen
    files = [f for f in os.listdir(LIB_PATH) if f.endswith(".md")]
    return sorted(files)

# --- 4. SIDOMENY ---
with st.sidebar:
    st.markdown("## 🎸 PlayIt! v3.2")
    låtar = get_songs()
    
    if not låtar:
        st.warning(f"Inga låtar hittades i: {LIB_PATH}")
        st.info("Lägg dina .md-filer i mappen 'library'.")
        val = "🏠 Hem"
    else:
        val = st.selectbox("Välj låt", ["🏠 Hem"] + låtar)

# --- 5. HUVUDVY ---
if val == "🏠 Hem":
    st.title("Välkommen till PlayIt!")
    st.write(f"Antal låtar i biblioteket: {len(låtar)}")
    if not låtar:
        st.error("Hittar inga låtar. Kontrollera att mappen 'library' innehåller .md-filer.")
else:
    file_path = os.path.join(LIB_PATH, val)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    st.markdown(f"<div class='song-title'>{val.replace('.md', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='song-sheet'>{content}</div>", unsafe_allow_html=True)