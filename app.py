import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. CONFIG & STATE ---
st.set_page_config(
    page_title="PlayIt! Pro",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initiera alla variabler i session_state
if "active_song" not in st.session_state:
    st.session_state.active_song = None
if "transpose_val" not in st.session_state:
    st.session_state.transpose_val = 0
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "is_scrolling" not in st.session_state:
    st.session_state.is_scrolling = False
if "scroll_speed" not in st.session_state:
    st.session_state.scroll_speed = 30

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK (TRANSPONERING & FILER) ---
def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
    return {f.replace('_', ' ').strip().title(): f for f in files}

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
    # Transponera ackord i klamrar [C] -> [D]
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    # Färglägg ackorden för display
    return re.sub(r"\[(.*?)\]", r'<span class="chord">[\1]</span>', text)

# --- 3. CSS (MASTER + PRO MIX) ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}

    /* HEADER & LOGO */
    .header-box {{
        position: fixed; top: 0; left: 0; width: 100%; height: 140px;
        background: #ffffff; z-index: 999; border-bottom: 2px solid #f0f0f0;
    }}
    .stage-logo {{
        position: fixed; left: 15px; top: 10px; height: 75px;
        z-index: 1000; transform: rotate(-5deg);
    }}

    /* START-KNAPP (TOP RIGHT) */
    .stButton > button[kind="secondary"] {{
        position: fixed !important; top: 20px !important; right: 15px !important;
        background: #000 !important; color: #fff !important;
        border-radius: 50px !important; z-index: 1001 !important;
    }}

    /* HORISONTELL LÅTRAD (SWIPE) */
    .song-nav {{
        position: fixed; top: 90px; left: 0; width: 100%;
        overflow-x: auto; white-space: nowrap; padding: 10px;
        z-index: 1002; background: #fff; display: flex; gap: 8px;
    }}

    /* LÅT-TEXT */
    .lyrics-area {{
        margin-top: 150px; margin-bottom: 200px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: {st.session_state.font_size}px !important;
        line-height: 1.4 !important; white-space: pre-wrap !important;
        color: #000 !important; padding: 0 20px;
    }}
    .chord {{ color: #6750A4; font-weight: 700; }}

    /* STICKY BOTTOM PANEL */
    .bottom-panel {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #f8f9fa; border-top: 2px solid #ddd;
        padding: 15px; z-index: 9999;
    }}

    /* Touch-knappar */
    .stButton > button {{ min-height: 44px !important; font-weight: 700 !important; }}
    
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER HEADER & NAV ---
st.markdown('<div class="header-box"></div>', unsafe_allow_html=True)

# Logga (Text-fallback)
st.markdown('<div class="stage-logo" style="font-weight:900; font-size:28px;">🎸 PLAYIT!</div>', unsafe_allow_html=True)

# START (Reset)
if st.button("START", key="reset", kind="secondary"):
    st.session_state.active_song = None
    st.session_state.transpose_val = 0
    st.session_state.is_scrolling = False
    st.rerun()

# LÅTARKIVET (Swajp-rad)
songs = get_songs()
st.markdown('<div style="height:90px"></div>', unsafe_allow_html=True) # Spacer
cols = st.columns(len(songs) if songs else 1)
for i, (name, stem) in enumerate(songs.items()):
    with cols[i]:
        if st.button(name.upper(), key=f"nav_{stem}"):
            st.session_state.active_song = stem
            st.session_state.transpose_val = 0 # Nollställ vid ny låt
            st.rerun()

# --- 5. LÅT-INNEHÅLL ---
if st.session_state.active_song:
    path = LIB_DIR / f"{st.session_state.active_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        display_html = process_content(raw_text, st.session_state.transpose_val)
        st.markdown(f'<div class="lyrics-area">{display_html}</div>', unsafe_allow_html=True)
    else:
        st.error("Filen saknas")

# --- 6. STICKY CONTROL PANEL ---
st.markdown('<div class="bottom-panel">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([1,1,1,2,1])

with c1:
    if st.button("–", key="t_down"):
        st.session_state.transpose_val -= 1
        st.rerun()
with c2:
    st.markdown(f"<center><small>TONE</small><br><b>{st.session_state.transpose_val}</b></center>", unsafe_allow_html=True)
with c3:
    if st.button("+", key="t_up"):
        st.session_state.transpose_val += 1
        st.rerun()
with c4:
    st.session_state.scroll_speed = st.slider("SCROLL", 0, 100, st.session_state.scroll_speed, label_visibility="collapsed")
with c5:
    lab = "STOP" if st.session_state.is_scrolling else "GO"
    if st.button(lab, key="sc_btn"):
        st.session_state.is_scrolling = not st.session_state.is_scrolling
        st.rerun()

# Rad för textstorlek
f1, f2, f3 = st.columns([1,2,1])
with f1: 
    if st.button("A–", key="f_down"): 
        st.session_state.font_size -= 2
        st.rerun()
with f3: 
    if st.button("A+", key="f_up"): 
        st.session_state.font_size += 2
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AUTO-SCROLL ENGINE ---
if st.session_state.is_scrolling and st.session_state.scroll_speed > 0:
    ms = int((101 - st.session_state.scroll_speed) / 2)
    st.components.v1.html(f"""
        <script>
        setInterval(function() {{ window.parent.window.scrollBy(0, 1); }}, {ms});
        </script>
    """, height=0)

# Scroll to top fix
if not st.session_state.is_scrolling and st.session_state.transpose_val == 0:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
