import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. GRUNDLÄGGANDE KONFIGURATION ---
st.set_page_config(
    page_title="PlayIt! Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initiera Session State
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 30

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK & HJÄLPFUNKTIONER ---
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
    # Transponera ackord [Am] -> [Bm]
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    # Färga ackorden lila/rosa för scenkontrast
    return re.sub(r"\[(.*?)\]", r'<b style="color:#D488FF;">[\1]</b>', text)

# --- 3. DEN AVANCERADE CSS-INJEKTIONEN (MOBILOPTIMERING) ---
st.markdown(f"""
<style>
    /* Nollställ Streamlit helt */
    [data-testid="stAppViewContainer"], .main, .stApp {{
        background-color: #000000 !important;
        color: #ffffff !important;
    }}
    [data-testid="stHeader"], footer, [data-testid="stToolbar"] {{ display: none !important; }}
    .main .block-container {{ 
        padding: 0 !important; 
        max-width: 100% !important; 
        margin: 0 !important;
    }}

    /* STICKY HEADER FÖR LOGGA */
    .sticky-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100px;
        background: #000; z-index: 1000;
        display: flex; justify-content: center; align-items: center;
        border-bottom: 1px solid #222;
    }}
    .logo-img {{ height: 80px; width: auto; object-fit: contain; }}

    /* STICKY FOOTER FÖR KONTROLLER */
    .sticky-footer {{
        position: fixed; bottom: 0; left: 0; width: 100%; height: 70px;
        background: #111; z-index: 1000;
        display: flex; justify-content: space-around; align-items: center;
        border-top: 1px solid #333; padding: 0 10px;
    }}

    /* LÅT-TEXT (MONOSPACE) */
    .song-display {{
        margin-top: 110px; /* Under headern */
        margin-bottom: 80px; /* Ovanför footern */
        padding: 20px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px;
        line-height: 1.5;
        white-space: pre-wrap;
        color: #cccccc;
    }}

    /* Göm de faktiska Streamlit-knapparna men behåll funktionaliteten */
    .stButton > button {{
        width: 100%; background: #222 !important; color: white !important;
        border: 1px solid #444 !important; font-weight: bold !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. RENDER LAYOUT ---

# HEADER
logo_data = get_logo_b64()
st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="logo-img">', unsafe_allow_html=True)
else:
    st.markdown('<h2 style="margin:0;">PLAYIT!</h2>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# NAVIGERING & INNEHÅLL
if not st.session_state.active_song:
    # --- LISTSIDA ---
    st.markdown('<div style="margin-top:120px; padding:20px;">', unsafe_allow_html=True)
    songs = get_songs()
    if not songs:
        st.warning("Inga låtar hittades i mappen 'library/'.")
    for name, stem in songs.items():
        if st.button(name, key=f"btn_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- LÅTSIDA ---
    # Renderar texten
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        processed_html = process_text(raw_text, st.session_state.transpose)
        st.markdown(f'<div class="song-display">{processed_html}</div>', unsafe_allow_html=True)
    
    # FOOTER KONTROLLER (Här tvingar vi rad-layout)
    st.markdown('<div class="sticky-footer">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([1,1,1,2,1.5])
    
    with f_col1:
        if st.button("–"): 
            st.session_state.transpose -= 1
            st.rerun()
    with f_col2:
        if st.button("STD"): 
            st.session_state.transpose = 0
            st.rerun()
    with f_col3:
        if st.button("+"): 
            st.session_state.transpose += 1
            st.rerun()
    with f_col4:
        label = "⏸ STOPP" if st.session_state.scrolling else "▶ SCROLL"
        if st.button(label, type="primary"):
            st.session_state.scrolling = not st.session_state.scrolling
            st.rerun()
    with f_col5:
        if st.button("STÄNG"):
            st.session_state.active_song = None
            st.session_state.scrolling = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. AVANCERAD SCROLL-MOTOR (JS) ---
if st.session_state.scrolling:
    # Beräkna hastighet: Högre fart = lägre delay
    # Vi använder en mjukare scroll-metod för att undvika ryckighet
    delay = int((105 - st.session_state.speed) / 2)
    st.components.v1.html(f"""
        <script>
        if (window.parent.scrollInterval) {{
            clearInterval(window.parent.scrollInterval);
        }}
        window.parent.scrollInterval = setInterval(function() {{
            window.parent.window.scrollBy({{
                top: 1,
                left: 0,
                behavior: 'smooth'
            }});
        }}, {delay});
        </script>
    """, height=0)
else:
    # Stoppa scroll om den är avstängd
    st.components.v1.html("""
        <script>
        if (window.parent.scrollInterval) {
            clearInterval(window.parent.scrollInterval);
        }
        </script>
    """, height=0)
