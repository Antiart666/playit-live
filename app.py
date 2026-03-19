import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(page_title="PlayIt!", layout="wide")

# Session State
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 35

LIB_DIR = Path("library")
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK ---
def get_songs():
    return {f.stem.replace('_', ' ').upper(): f.stem for f in LIB_DIR.glob("*.md")}

def get_logo_b64():
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

# --- 3. CSS (STAGE READY) ---
st.markdown(f"""
<style>
    /* Svart tema & Nollställ marginaler */
    [data-testid="stAppViewContainer"], .main, .stApp {{ background-color: #000 !important; color: #fff !important; }}
    [data-testid="stHeader"], footer {{ display: none !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* Stor centrerad logga */
    .header-container {{
        width: 100%; padding: 20px 0; text-align: center; background: #000;
        border-bottom: 1px solid #222;
    }}
    .big-logo {{ height: 120px; width: auto; }}

    /* Kontrollraden - Snygg och smal */
    .control-bar {{
        background: #111; padding: 10px 0; border-bottom: 1px solid #333;
        display: flex; justify-content: center; gap: 10px;
    }}

    /* Låt-text */
    .song-text {{
        padding: 20px; font-family: 'Courier New', monospace; font-size: 18px;
        line-height: 1.5; white-space: pre-wrap; color: #eee; background: #000;
    }}

    /* Streamlit Button Styling */
    .stButton > button {{
        background: #222 !important; color: white !important;
        border: 1px solid #444 !important; border-radius: 8px !important;
        font-weight: bold !important; text-transform: uppercase !important;
    }}
    button[kind="primary"] {{ background: #bb86fc !important; color: #000 !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER (LOGGA) ---
logo_data = get_logo_b64()
st.markdown('<div class="header-container">', unsafe_allow_html=True)
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="big-logo">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. NAVIGATION ---

if not st.session_state.active_song:
    # LISTSIDA
    st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=f"list_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # LÅTSIDA - KONTROLLER
    c1, c2, c3, c4, c5 = st.columns([1,1,1,2,1])
    with c1:
        if st.button("–"): st.session_state.transpose -= 1; st.rerun()
    with c2:
        if st.button("STD"): st.session_state.transpose = 0; st.rerun()
    with c3:
        if st.button("+"): st.session_state.transpose += 1; st.rerun()
    with c4:
        lab = "STOPP" if st.session_state.scrolling else "SCROLL"
        if st.button(lab, type="primary", use_container_width=True):
            st.session_state.scrolling = not st.session_state.scrolling
            st.rerun()
    with c5:
        if st.button("LÅTAR"):
            st.session_state.active_song = None
            st.session_state.scrolling = False
            st.rerun()

    # RENDERA LÅT
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            text = process_text(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="song-text">{text}</div>', unsafe_allow_html=True)

# --- 6. SCROLL ENGINE ---
if st.session_state.scrolling:
    ms = int((105 - st.session_state.speed) / 2)
    st.components.v1.html(f"<script>setInterval(()=>window.parent.window.scrollBy(0,1),{ms})</script>", height=0)
