import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

for key, val in {"active_song": None, "transpose_val": 0, "font_size": 22, "is_scrolling": False, "scroll_speed": 40}.items():
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

# --- 3. CSS (DEN AGGRESSIVA FIXEN) ---
st.markdown(f"""
    <style>
    /* Ta bort Streamlits standardmarginaler helt */
    [data-testid="stAppViewContainer"] {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; margin-top: -50px !important; }}
    
    /* FAST HEADER - GÖR LOGGAN STÖRRE HÄR (90px) */
    .top-nav {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100px;
        background: white; border-bottom: 2px solid #eee;
        z-index: 999999; display: flex; align-items: center; padding: 0 15px;
    }}
    
    .logo-container {{ flex-grow: 1; display: flex; align-items: center; }}
    .logo-img {{ height: 85px; width: auto; }} /* Ökad storlek */
    .logo-txt {{ font-size: 35px; font-weight: 900; color: black; }}

    /* KONTROLL-PANEL */
    .control-panel {{
        position: fixed; top: 100px; left: 0; width: 100%; height: 70px;
        background: #fdfdfd; border-bottom: 1px solid #ddd;
        z-index: 999998; display: flex; align-items: center;
    }}

    /* POSITIONERING AV TEXT */
    .list-container {{ margin-top: 120px; padding: 20px; }}
    .song-container {{ 
        margin-top: 180px; padding: 20px 20px 150px 20px; 
        font-family: 'Roboto Mono', monospace; font-size: {st.session_state.font_size}px; 
        line-height: 1.4; white-space: pre-wrap; color: black;
    }}

    /* KNAPP-STYLING */
    .stButton > button {{ border-radius: 12px !important; font-weight: 800 !important; }}
    
    /* Fix för BACK-knappen så den inte hamnar under loggan */
    div.stButton > button[kind="secondary"] {{
        background: black !important; color: white !important;
        border-radius: 50px !important; height: 45px !important; width: 110px !important;
        position: fixed; top: 25px; right: 15px; z-index: 1000000;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION & HEADER ---
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
logo_data = get_logo_b64()
if logo_data:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_data}" class="logo-img"></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="logo-container"><span class="logo-txt">PLAYIT!</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# BACK-knapp (LÅTAR)
if st.session_state.active_song:
    if st.button("LÅTAR", key="back_btn", type="secondary"):
        st.session_state.active_song = None
        st.session_state.is_scrolling = False
        st.rerun()

# --- 5. INNEHÅLL ---
if not st.session_state.active_song:
    st.markdown('<div class="list-container">', unsafe_allow_html=True)
    st.markdown("## MINA LÅTAR")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name.upper(), key=f"btn_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Kontrollpanel
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        if st.button("–", key="t-"): st.session_state.transpose_val -= 1; st.rerun()
    with c2:
        if st.button("STD", key="std"): st.session_state.transpose_val = 0; st.rerun()
    with c3:
        if st.button("+", key="t+"): st.session_state.transpose_val += 1; st.rerun()
    with c4:
        label = "⏸" if st.session_state.is_scrolling else "▶"
        if st.button(label, key="sc_sw", type="primary"): 
            st.session_state.is_scrolling = not st.session_state.is_scrolling
            st.rerun()
    with c5:
        if st.button("S-"): st.session_state.scroll_speed = max(5, st.session_state.scroll_speed - 5); st.rerun()
    with c6:
        if st.button("S+"): st.session_state.scroll_speed = min(100, st.session_state.scroll_speed + 5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Låten
    path = LIB_DIR / f"{st.session_state.active_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            lyrics = process_content(f.read(), st.session_state.transpose_val)
        st.markdown(f'<div class="song-container">{lyrics}</div>', unsafe_allow_html=True)

# --- 6. SCROLL ENGINE ---
if st.session_state.is_scrolling:
    ms = int((105 - st.session_state.scroll_speed) / 2)
    st.components.v1.html(f"<script>setInterval(()=>window.parent.window.scrollBy(0,1),{ms})</script>", height=0)
