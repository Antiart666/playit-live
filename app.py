import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

# Session State
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

# --- 3. CSS (BRUTAL OVERRIDE) ---
# Vi nollställer ALLA marginaler som Streamlit lägger till automatiskt
st.markdown(f"""
    <style>
    /* Nollställ Streamlits tomrum i toppen */
    [data-testid="stAppViewContainer"] {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}

    /* FIXERAD LOGGA - LÄNGST UPP TILL VÄNSTER */
    .fixed-logo-container {{
        position: fixed; top: 10px; left: 15px; width: 180px; height: 80px;
        z-index: 10001; display: flex; align-items: center;
    }}
    .logo-img {{ height: 70px; width: auto; object-fit: contain; }}
    .logo-fallback {{ font-weight: 900; font-size: 35px; color: #000; letter-spacing: -1px; }}

    /* LÅTAR-KNAPP - LÄNGST UPP TILL HÖGER */
    .back-btn-box {{
        position: fixed; top: 20px; right: 15px; z-index: 10002;
    }}
    div.stButton > button[kind="secondary"] {{
        background: #000 !important; color: #fff !important;
        border-radius: 50px !important; font-weight: 800 !important;
        padding: 0 20px !important; height: 45px !important; border: none !important;
    }}

    /* KONTROLL-PANEL (RADEN UNDER LOGGAN) */
    .controls-wrapper {{
        position: fixed; top: 95px; left: 0; width: 100%; height: 60px;
        background: #ffffff; border-bottom: 2px solid #f0f0f0;
        z-index: 10000; display: flex; align-items: center;
    }}

    /* TEXT & LISTA POSITIONERING */
    .list-view {{ margin-top: 100px; padding: 20px; }}
    .song-view {{ 
        margin-top: 165px; padding: 20px 20px 200px 20px; 
        font-family: 'Roboto Mono', monospace; 
        font-size: {st.session_state.font_size}px; 
        line-height: 1.4; white-space: pre-wrap; color: #000;
    }}

    /* Touch-fix för knappar */
    .stButton > button {{ border-radius: 10px !important; font-weight: 800 !important; }}
    
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER STATIC ELEMENTS ---

# Logga (Alltid synlig)
st.markdown('<div class="fixed-logo-container">', unsafe_allow_html=True)
logo_b64 = get_logo_b64()
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
else:
    st.markdown('<span class="logo-fallback">PLAYIT!</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. NAVIGATION ---

if not st.session_state.active_song:
    # --- SIDA 1: LÅTLISTAN ---
    st.markdown('<div class="list-view">', unsafe_allow_html=True)
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name.upper(), key=f"L_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.transpose_val = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- SIDA 2: SPEL-LÄGE ---
    # LÅTAR-knapp (Back)
    st.markdown('<div class="back-btn-box">', unsafe_allow_html=True)
    if st.button("LÅTAR", key="back_cmd", type="secondary"):
        st.session_state.active_song = None
        st.session_state.is_scrolling = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Kontroll-rad (Transp & Scroll)
    st.markdown('<div class="controls-wrapper">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,1])
    with c1:
        if st.button("–", key="t-"): st.session_state.transpose_val -= 1; st.rerun()
    with c2:
        if st.button("STD", key="t0"): st.session_state.transpose_val = 0; st.rerun()
    with c3:
        if st.button("+", key="t+"): st.session_state.transpose_val += 1; st.rerun()
    with c4:
        sc_icon = "⏸" if st.session_state.is_scrolling else "▶"
        if st.button(sc_icon, key="sc_toggle", type="primary"): 
            st.session_state.is_scrolling = not st.session_state.is_scrolling
            st.rerun()
    with c5:
        if st.button("S-"): st.session_state.scroll_speed = max(5, st.session_state.scroll_speed - 5); st.rerun()
    with c6:
        if st.button("S+"): st.session_state.scroll_speed = min(100, st.session_state.scroll_speed + 5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Låttexten
    path = LIB_DIR / f"{st.session_state.active_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw_lyrics = f.read()
        lyrics_html = process_content(raw_lyrics, st.session_state.transpose_val)
        st.markdown(f'<div class="song-view">{lyrics_html}</div>', unsafe_allow_html=True)
    else:
        st.error(f"Kunde inte hitta {st.session_state.active_song}.md")

# --- 6. SCROLL ENGINE ---
if st.session_state.is_scrolling:
    ms = int((105 - st.session_state.scroll_speed) / 2)
    st.components.v1.html(f"<script>setInterval(()=>window.parent.window.scrollBy(0,1),{ms})</script>", height=0)

# Reset scroll fix
if st.session_state.active_song and not st.session_state.is_scrolling and st.session_state.transpose_val == 0:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
