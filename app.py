import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. SETUP ---
st.set_page_config(page_title="PlayIt!", layout="wide")

# Session State
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 40

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)

# --- 2. FUNKTIONER ---
def get_songs():
    return {f.stem.replace('_', ' ').title(): f.stem for f in LIB_DIR.glob("*.md")}

def transpose_chord(chord, steps):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    match = re.match(r"([A-G]#?)(.*)", chord)
    if not match: return chord
    root, suffix = match.groups()
    if root not in notes: return chord
    return f"{notes[(notes.index(root) + steps) % 12]}{suffix}"

def process_text(text, steps):
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    return re.sub(r"\[(.*?)\]", r'<b style="color:#6750A4;">[\1]</b>', text)

# --- 3. CSS (DENNA GÅNGEN HELT UTAN KRUSIDULLER) ---
st.markdown("""
<style>
    /* Ta bort allt skräp från Streamlit */
    [data-testid="stHeader"], footer {display: none !important;}
    .main .block-container {padding: 0 !important; max-width: 100% !important;}
    
    /* Enkel Header */
    .app-header {
        background: #fff; padding: 10px; border-bottom: 2px solid #000;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 999;
    }
    
    /* Texten */
    .song-content {
        padding: 20px; font-family: monospace; font-size: 20px;
        white-space: pre-wrap; line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. RENDER ---

# HEADER
header_html = f"""
<div class="app-header">
    <h1 style="margin:0; font-size:24px;">🎸 PLAYIT!</h1>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

if not st.session_state.active_song:
    # LISTSIDA
    st.write("### VÄLJ LÅT")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name.upper(), key=stem, use_container_width=True):
            st.session_state.active_song = stem
            st.rerun()
else:
    # LÅTSIDA
    # Back-knapp högst upp
    if st.button("⬅ TILLBAKA", use_container_width=True):
        st.session_state.active_song = None
        st.session_state.scrolling = False
        st.rerun()

    # Kontroller (enkelt placerade)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("– TONE"): st.session_state.transpose -= 1; st.rerun()
    with c2:
        if st.button("STD"): st.session_state.transpose = 0; st.rerun()
    with c3:
        if st.button("+ TONE"): st.session_state.transpose += 1; st.rerun()

    c4, c5 = st.columns(2)
    with c4:
        label = "STOPP" if st.session_state.scrolling else "SCROLLA"
        if st.button(label, type="primary", use_container_width=True):
            st.session_state.scrolling = not st.session_state.scrolling
            st.rerun()
    with c5:
        st.session_state.speed = st.slider("Fart", 1, 100, st.session_state.speed)

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
