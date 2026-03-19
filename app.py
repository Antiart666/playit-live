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

# Säkerställ att alla variabler finns i session_state
defaults = {
    "active_song": None,
    "transpose_val": 0,
    "font_size": 18,
    "is_scrolling": False,
    "scroll_speed": 30
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)

# --- 2. LOGIK (SÄKERHETSOPTIMERAD) ---
def get_songs():
    """Hämtar låtar och skapar säkra unika nycklar."""
    try:
        files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
        # Skapa en dict: { "Snyggt Namn": "filnamn_utan_konstiga_tecken" }
        return {f.replace('_', ' ').strip().title(): f for f in files}
    except Exception:
        return {}

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
    # Färglägg ackorden för display (Material Purple)
    return re.sub(r"\[(.*?)\]", r'<span style="color:#6750A4; font-weight:700;">[\1]</span>', text)

# --- 3. CSS (FIXERAD LAYOUT) ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}

    /* HEADER */
    .header-box {{
        position: fixed; top: 0; left: 0; width: 100%; height: 140px;
        background: #ffffff; z-index: 999; border-bottom: 2px solid #f0f0f0;
    }}

    /* START-KNAPP (TOP RIGHT) */
    div.stButton > button[kind="secondary"] {{
        position: fixed !important; top: 20px !important; right: 15px !important;
        background: #000 !important; color: #fff !important;
        border-radius: 50px !important; z-index: 1001 !important;
        padding: 0 25px !important; height: 45px !important;
    }}

    /* SWIPE-RAD */
    .song-nav-wrapper {{
        position: fixed; top: 85px; left: 0; width: 100%;
        overflow-x: auto; z-index: 1002; background: #fff;
        padding: 10px 15px; border-bottom: 1px solid #eee;
    }}

    /* TEXT-AREA */
    .lyrics-area {{
        margin-top: 160px; margin-bottom: 220px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: {st.session_state.font_size}px !important;
        line-height: 1.5 !important; white-space: pre-wrap !important;
        color: #000 !important; padding: 0 20px;
    }}

    /* BOTTOM PANEL */
    .bottom-panel {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #f8f9fa; border-top: 2px solid #ddd;
        padding: 15px; z-index: 9999;
    }}

    /* Touch-fix för alla knappar */
    button {{ min-height: 44px !important; }}
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER UI ---

st.markdown('<div class="header-box"></div>', unsafe_allow_html=True)
st.markdown('<div style="position:fixed; left:15px; top:20px; font-weight:900; font-size:24px; z-index:1000;">🎸 PLAYIT!</div>', unsafe_allow_html=True)

# START (Reset)
if st.button("START", key="global_reset", kind="secondary"):
    st.session_state.active_song = None
    st.session_state.transpose_val = 0
    st.session_state.is_scrolling = False
    st.rerun()

# LÅTARKIV (Säker rendering)
songs = get_songs()
st.markdown('<div style="height:85px"></div>', unsafe_allow_html=True) 

if songs:
    # Vi använder st.columns för att behålla farten, men med unika keys
    cols = st.columns(len(songs))
    for i, (name, stem) in enumerate(songs.items()):
        with cols[i]:
            # NYCKEL-FIX: btn_ + filnamn garanterar unikhet
            if st.button(name.upper(), key=f"btn_{stem}"):
                st.session_state.active_song = stem
                st.session_state.transpose_val = 0
                st.session_state.is_scrolling = False
                st.rerun()

# --- 5. DISPLAY ---
if st.session_state.active_song:
    path = LIB_DIR / f"{st.session_state.active_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = process_content(f.read(), st.session_state.transpose_val)
        st.markdown(f'<div class="lyrics-area">{content}</div>', unsafe_allow_html=True)

# --- 6. BOTTOM PANEL ---
st.markdown('<div class="bottom-panel">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([1,1,1,2,1])

with c1:
    if st.button("–", key="transp_down"):
        st.session_state.transpose_val -= 1
        st.rerun()
with c2:
    st.markdown(f"<center><small>TONE</small><br><b>{st.session_state.transpose_val}</b></center>", unsafe_allow_html=True)
with c3:
    if st.button("+", key="transp_up"):
        st.session_state.transpose_val += 1
        st.rerun()
with c4:
    st.session_state.scroll_speed = st.slider("SCROLL", 0, 100, st.session_state.scroll_speed, label_visibility="collapsed")
with c5:
    btn_label = "STOP" if st.session_state.is_scrolling else "GO"
    if st.button(btn_label, key="toggle_scroll"):
        st.session_state.is_scrolling = not st.session_state.is_scrolling
        st.rerun()

# Textstorlek rad
f1, f2, f3 = st.columns([1,2,1])
with f1: 
    if st.button("A–", key="size_down"): 
        st.session_state.font_size -= 2
        st.rerun()
with f3: 
    if st.button("A+", key="size_up"): 
        st.session_state.font_size += 2
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AUTO-SCROLL ---
if st.session_state.is_scrolling and st.session_state.scroll_speed > 0:
    # 101 - speed ger lägre siffra för högre fart (ms delay)
    ms = int((101 - st.session_state.scroll_speed) / 2)
    st.components.v1.html(f"""
        <script>
        setInterval(function() {{ window.parent.window.scrollBy(0, 1); }}, {ms});
        </script>
    """, height=0)

# Reset scroll position
if st.session_state.active_song and not st.session_state.is_scrolling and st.session_state.transpose_val == 0:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
