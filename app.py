import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide")

# Session State för att hålla koll på inställningar
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 30
if "font_size" not in st.session_state: st.session_state.font_size = 18

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK ---
def get_songs():
    return {f.stem.replace('_', ' ').title(): f.stem for f in LIB_DIR.glob("*.md")}

def get_logo():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def transpose_chord(chord, steps):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    match = re.match(r"([A-G]#?)(.*)", chord)
    if not match: return chord
    root, suffix = match.groups()
    if root not in notes: return chord
    return f"{notes[(notes.index(root) + steps) % 12]}{suffix}"

def process_text(text, steps):
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    return re.sub(r"\[(.*?)\]", r'<b style="color:#bb86fc;">[\1]</b>', text)

# --- 3. CSS (BLACK STAGE THEME) ---
st.markdown(f"""
<style>
    /* Scen-läge: Svart bakgrund */
    [data-testid="stAppViewContainer"], .main, .stApp {{
        background-color: #000000 !important;
        color: #ffffff !important;
    }}
    [data-testid="stHeader"], footer {{display: none !important;}}
    .main .block-container {{padding: 0 !important;}}

    /* Kompakt Header */
    .app-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: #121212; border-bottom: 1px solid #333;
        display: flex; align-items: center; padding: 0 10px; z-index: 9999;
    }}
    .logo-img {{ height: 40px; margin-right: 10px; }}
    
    /* Låt-texten */
    .song-content {{
        margin-top: 120px; padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        font-size: {st.session_state.font_size}px;
        line-height: 1.5; white-space: pre-wrap; color: #eee;
    }}
    
    /* Göm Streamlits fula widgets */
    .stButton > button {{
        background: #333 !important; color: white !important;
        border: 1px solid #444 !important; height: 35px !important;
        font-size: 12px !important; padding: 0 5px !important;
    }}
    div[data-testid="stVerticalBlock"] > div {{ padding: 0 !important; gap: 0 !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---

# HEADER
logo_b64 = get_logo()
st.markdown('<div class="app-header">', unsafe_allow_html=True)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
st.markdown('<span style="font-weight:900;">PLAYIT!</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.active_song:
    # --- LISTSIDA ---
    st.markdown('<div style="margin-top:80px; padding:20px;">', unsafe_allow_html=True)
    st.write("### REPERTOAR")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name.upper(), key=stem, use_container_width=True):
            st.session_state.active_song = stem
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- LÅTSIDA (Kompakt kontrollrad högst upp) ---
    # Vi lägger kontrollerna i en rad direkt under headern
    ctrl_row = st.container()
    with ctrl_row:
        st.markdown('<div style="position:fixed; top:60px; width:100%; background:#1e1e1e; z-index:9998; padding:5px 0;">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,2,1,1])
        with c1: 
            if st.button("–"): st.session_state.transpose -= 1; st.rerun()
        with c2: 
            if st.button("STD"): st.session_state.transpose = 0; st.rerun()
        with c3: 
            if st.button("+"): st.session_state.transpose += 1; st.rerun()
        with c4: 
            label = "STOP" if st.session_state.scrolling else "SCROLL"
            if st.button(label, type="primary"): st.session_state.scrolling = not st.session_state.scrolling; st.rerun()
        with c5:
            if st.button("LÅTAR"): st.session_state.active_song = None; st.session_state.scrolling = False; st.rerun()
        with c6:
            st.markdown(f"<center><small>T:{st.session_state.transpose}</small></center>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Innehåll
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = process_text(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="song-content">{full_text}</div>', unsafe_allow_html=True)

# --- 5. SCROLL ---
if st.session_state.scrolling:
    ms = int((105 - st.session_state.speed) / 2)
    st.components.v1.html(f"<script>setInterval(()=>window.parent.window.scrollBy(0,1),{ms})</script>", height=0)
