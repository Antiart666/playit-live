import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. CONFIG & STATE ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

# Session State Setup
for key, val in {
    "active_song": None, "transpose_val": 0, "font_size": 22, 
    "is_scrolling": False, "scroll_speed": 40}.items():
    if key not in st.session_state: st.session_state[key] = val

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK ---
def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
    return {f.replace('_', ' ').strip().title(): f for f in files}

def get_logo_b64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def transpose_chord(chord, steps):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    pattern = r"([A-G]#?)(.*)"
    match = re.match(pattern, chord)
    if not match: return chord
    root, suffix = match.groups()
    if root not in notes: return chord
    new_index = (notes.index(root) + steps) % 12
    return f"{notes[new_index]}{suffix}"

def process_content(text, steps):
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    return re.sub(r"\[(.*?)\]", r'<span style="color:#6750A4; font-weight:900;">[\1]</span>', text)

# --- 3. CSS (HARDCODED LAYOUT) ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}

    /* FIXED HEADER BOX */
    .fixed-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 110px;
        background: #ffffff; z-index: 9999; border-bottom: 2px solid #eee;
        display: flex; align-items: center; padding: 0 15px;
    }}

    .logo-img {{ height: 80px; width: auto; }}
    .logo-text {{ font-weight: 900; font-size: 32px; color: #000; }}

    /* BACK BUTTON (LÅTAR) */
    .back-btn-container {{
        position: fixed; top: 25px; right: 15px; z-index: 10000;
    }}

    /* CONTROL BAR (UNDER HEADER) */
    .control-bar {{
        position: fixed; top: 110px; left: 0; width: 100%; height: 60px;
        background: #fdfdfd; z-index: 9998; border-bottom: 1px solid #ddd;
        display: flex; justify-content: space-around; align-items: center;
    }}

    /* CONTENT AREAS */
    .list-area {{ margin-top: 120px; padding: 15px; }}
    .song-area {{ margin-top: 185px; padding: 0 20px 150px 20px; 
                  font-family: 'Roboto Mono', monospace; font-size: {st.session_state.font_size}px; 
                  line-height: 1.4; white-space: pre-wrap; }}

    /* STYLING FOR BUTTONS */
    .stButton > button {{ border-radius: 12px !important; font-weight: 800 !important; height: 45px !important; }}
    button[kind="secondary"] {{ background: #000 !important; color: #fff !important; border-radius: 50px !important; }}
    
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER RENDERING ---
st.markdown('<div class="fixed-header">', unsafe_allow_html=True)
logo_b64 = get_logo_b64()
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
else:
    st.markdown('<span class="logo-text">PLAYIT!</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. NAVIGATION LOGIK ---

if not st.session_state.active_song:
    # --- SIDA 1: LÅTLISTAN ---
    st.markdown('<div class="list-area">', unsafe_allow_html=True)
    st.markdown("### MINA LÅTAR")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name.upper(), key=f"list_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.transpose_val = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- SIDA 2: LÅTEN ---
    # LÅTAR (Back-knapp) längst upp till höger
    with st.container():
        st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
        if st.button("LÅTAR", key="back_btn", type="secondary"):
            st.session_state.active_song = None
            st.session_state.is_scrolling = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # KONTROLL-RADEN (Sitter alltid under loggan)
    st.markdown('<div class="control-bar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,1])
    with col1:
        if st.button("–", key="t-"): st.session_state.transpose_val -= 1; st.rerun()
    with col2:
        if st.button("STD", key="t0"): st.session_state.transpose_val = 0; st.rerun()
    with col3:
        if st.button("+", key="t+"): st.session_state.transpose_val += 1; st.rerun()
    with col4:
        scroll_icon = "⏸" if st.session_state.is_scrolling else "▶"
        if st.button(scroll_icon, key="sc_sw", type="primary"): 
            st.session_state.is_scrolling = not st.session_state.is_scrolling
            st.rerun()
    with col5:
        if st.button("S-"): st.session_state.scroll_speed = max(5, st.session_state.scroll_speed - 5); st.rerun()
    with col6:
        if st.button("S+"): st.session_state.scroll_speed = min(100, st.session_state.scroll_speed + 5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # RENDERA TEXT
    path = LIB_DIR / f"{st.session_state.active_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            lyrics = process_content(f.read(), st.session_state.transpose_val)
        st.markdown(f'<div class="song-area">{lyrics}</div>', unsafe_allow_html=True)

# --- 6. SCROLL ENGINE ---
if st.session_state.is_scrolling:
    ms = int((105 - st.session_state.scroll_speed) / 2)
    st.components.v1.html(f"<script>setInterval(()=>window.parent.window.scrollBy(0,1),{ms})</script>", height=0)

# Scroll till toppen vid ny låt
if st.session_state.active_song and not st.session_state.is_scrolling and st.session_state.transpose_val == 0:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
