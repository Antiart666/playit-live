import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. SETUP ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

# Session State
if "page" not in st.session_state: st.session_state.page = "list"
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 30

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. FUNKTIONER ---
def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
    return {f.replace('_', ' ').strip().upper(): f for f in files}

def get_logo_b64():
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except: return None
    return None

def transpose_chord(chord, steps):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    match = re.match(r"([A-G]#?)(.*)", chord)
    if not match: return chord
    root, suffix = match.groups()
    if root not in notes: return chord
    return f"{notes[(notes.index(root) + steps) % 12]}{suffix}"

def process_content(text, steps):
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    return re.sub(r"\[(.*?)\]", r'<b style="color:#D187FF;">[\1]</b>', text)

# --- 3. CSS (FÖR ATT DÖDA ERROR OCH FIXA LAYOUT) ---
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="top-logo">' if logo_b64 else '<b class="top-logo">PI!</b>'

st.markdown(f"""
<style>
    /* Svart bakgrund och nollställning */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{ background-color: #000 !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* FIXED HEADER */
    .nav-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: #111; z-index: 9999; border-bottom: 1px solid #333;
        display: flex; align-items: center; padding: 0 10px;
    }}
    .top-logo {{ height: 35px; width: auto; margin-right: 15px; }}

    /* LYRICS AREA */
    .lyrics-box {{
        margin-top: 80px; padding: 20px; padding-bottom: 100px;
        font-family: 'Courier New', monospace !important;
        font-size: 20px; line-height: 1.6; white-space: pre-wrap;
        color: #eee;
    }}

    /* KNAPPAR */
    .stButton > button {{
        background: #222 !important; color: #fff !important;
        border: 1px solid #444 !important;
    }}
</style>
<div class="nav-header">{logo_html}</div>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---

if st.session_state.page == "list":
    st.markdown('<div class="lyrics-box">', unsafe_allow_html=True)
    st.write("### REPERTOAR")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=stem, use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.page = "lyrics"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # LÅTVY - HEADER KONTROLLER
    c1, c2, c3 = st.columns([2, 4, 1])
    with c1:
        st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
        if st.button("⬅ LÅTAR"):
            st.session_state.page = "list"
            st.session_state.scrolling = False
            st.rerun()
    with c2:
        st.markdown(f"<p style='text-align:center; line-height:60px; margin:0; color:#888;'>{st.session_state.active_song.replace('_',' ')}</p>", unsafe_allow_html=True)
    with c3:
        with st.popover("⚙️"):
            st.write("TON")
            col_t1, col_t2 = st.columns(2)
            if col_t1.button("–"): st.session_state.transpose -= 1; st.rerun()
            if col_t2.button("+"): st.session_state.transpose += 1; st.rerun()
            if st.button("STD"): st.session_state.transpose = 0; st.rerun()
            st.divider()
            st.session_state.speed = st.slider("FART", 1, 100, st.session_state.speed)
            if st.button("START/STOPP", type="primary", use_container_width=True):
                st.session_state.scrolling = not st.session_state.scrolling
                st.rerun()

    # RENDER TEXT
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            text = process_content(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="lyrics-box">{text}</div>', unsafe_allow_html=True)

# --- 5. SCROLL MOTOR (DENNA FIXAR SCRIPT ERROR) ---
if st.session_state.scrolling:
    # Beräkna hastighet: 100 i appen ger ca 10ms delay (snabbt)
    delay = int(110 - st.session_state.speed)
    st.components.v1.html(f"""
        <script>
        // Vi använder 'window.parent' för att nå huvudfönstret från iframen
        const scrollStep = () => {{
            if (window.parent.window) {{
                window.parent.window.scrollBy(0, 1);
            }}
        }};
        
        // Rensa gamla intervaller för att inte dubbel-scrolla
        if (window.parent.myScrollInterval) {{
            clearInterval(window.parent.myScrollInterval);
        }}
        
        window.parent.myScrollInterval = setInterval(scrollStep, {delay});
        </script>
    """, height=0)
else:
    st.components.v1.html("""
        <script>
        if (window.parent.myScrollInterval) {
            clearInterval(window.parent.myScrollInterval);
        }
        </script>
    """, height=0)
