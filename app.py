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

# Initiera alla variabler för att slippa NameError/KeyError
defaults = {
    "active_song": None,
    "transpose_val": 0,
    "font_size": 22,
    "is_scrolling": False,
    "scroll_speed": 40
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK ---
def get_songs():
    try:
        files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
        return {f.replace('_', ' ').strip().title(): f for f in files}
    except: return {}

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
    # Transponera ackord i [Klamrar]
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    # Färglägg ackorden för tydlighet (Material Purple)
    return re.sub(r"\[(.*?)\]", r'<span style="color:#6750A4; font-weight:900;">[\1]</span>', text)

# --- 3. CSS (CLEAN STAGE DESIGN) ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}

    /* HEADER */
    .header-box {{
        position: fixed; top: 0; left: 0; width: 100%; height: 115px;
        background: #ffffff; z-index: 999; border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (VÄNSTER) */
    .stage-logo {{
        position: fixed; left: 15px; top: 10px; height: 85px; z-index: 1000;
    }}

    /* LÅTAR / BACK-KNAPP (TOP RIGHT) */
    div.stButton > button[data-testid="baseButton-secondary"] {{
        position: fixed !important; top: 20px !important; right: 15px !important;
        background: #000 !important; color: #fff !important;
        border-radius: 50px !important; z-index: 1001 !important;
        padding: 0 25px !important; height: 45px !important; font-weight: 800 !important;
    }}

    /* KONTROLL-RADEN (UNDER HEADERN) */
    .control-row {{
        position: fixed; top: 115px; left: 0; width: 100%;
        background: #fdfdfd; z-index: 998; border-bottom: 1px solid #eee;
        padding: 5px 0;
    }}

    /* LÅT-TEXT */
    .lyrics-area {{
        margin-top: 180px; margin-bottom: 100px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: {st.session_state.font_size}px !important;
        line-height: 1.4 !important; white-space: pre-wrap !important;
        color: #000 !important; padding: 0 20px;
    }}

    /* Knappar-generellt */
    button {{ min-height: 44px !important; border-radius: 10px !important; font-weight: 800 !important; }}
    
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RENDER UI ---

# Header & Logga
st.markdown('<div class="header-box"></div>', unsafe_allow_html=True)
logo_b64 = get_logo_b64()
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:15px; top:25px; font-weight:900; font-size:28px; z-index:1000;">🎸 PLAYIT!</div>', unsafe_allow_html=True)

# --- NAVIGATION ---

if not st.session_state.active_song:
    # SIDA 1: LÅTLISTAN
    st.markdown('<div style="margin-top:120px; padding:20px;">', unsafe_allow_html=True)
    st.write("### VÄLJ LÅT")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(f" {name.upper()} ", key=f"sel_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.transpose_val = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # SIDA 2: LÅTEN
    # LÅTAR (Back-knapp)
    if st.button("LÅTAR", type="secondary"):
        st.session_state.active_song = None
        st.session_state.is_scrolling = False
        st.rerun()

    # KONTROLL-RADEN (Transponering & Scroll)
    st.markdown('<div class="control-row">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 1, 1])
    
    with c1: # Transp NER
        if st.button("–", key="t_dn"): st.session_state.transpose_val -= 1; st.rerun()
    with c2: # STD / RESET
        if st.button("STD", key="t_std"): st.session_state.transpose_val = 0; st.rerun()
    with c3: # Transp UPP
        if st.button("+", key="t_up"): st.session_state.transpose_val += 1; st.rerun()
    with c4: # Scroll ON/OFF
        label = "⏸" if st.session_state.is_scrolling else "▶"
        if st.button(label, key="sc_toggle", type="primary"):
            st.session_state.is_scrolling = not st.session_state.is_scrolling
            st.rerun()
    with c5: # Fart NER
        if st.button("S-"): st.session_state.scroll_speed = max(5, st.session_state.scroll_speed - 5); st.rerun()
    with c6: # Fart UPP
        if st.button("S+"): st.session_state.scroll_speed = min(100, st.session_state.scroll_speed + 5); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # RENDERA LÅTTEXTEN
    path = LIB_DIR / f"{st.session_state.active_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = process_content(f.read(), st.session_state.transpose_val)
        st.markdown(f'<div class="lyrics-area">{content}</div>', unsafe_allow_html=True)

# --- 5. AUTO-SCROLL ENGINE ---
if st.session_state.is_scrolling and st.session_state.scroll_speed > 0:
    ms = int((105 - st.session_state.scroll_speed) / 2)
    st.components.v1.html(f"""
        <script>
        setInterval(function() {{ window.parent.window.scrollBy(0, 1); }}, {ms});
        </script>
    """, height=0)

# Reset scroll vid ny låt
if st.session_state.active_song and not st.session_state.is_scrolling and st.session_state.transpose_val == 0:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
