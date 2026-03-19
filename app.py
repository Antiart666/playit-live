import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. KONFIGURATION & INITIALISERING ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state: st.session_state.page = "library"
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 30

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. HJÄLPFUNKTIONER ---
def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
    return {f.replace('_', ' ').strip().upper(): f for f in files}

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

def process_lyrics(text, steps):
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    return re.sub(r"\[(.*?)\]", r'<b style="color:#D187FF;">[\1]</b>', text)

# --- 3. CSS HACK (ELIMINERA STREAMLIT UI) ---
logo_b64 = get_logo_b64()
logo_tag = f'<img src="data:image/png;base64,{logo_b64}" style="height:30px;">' if logo_b64 else '<b style="color:white;">PI!</b>'

st.markdown(f"""
<style>
    /* Dölj Streamlits fasta element */
    header, [data-testid="stHeader"], footer, [data-testid="stToolbar"] {{
        display: none !important;
    }}
    
    /* Svart scen-bakgrund och nollställd padding */
    [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    .main .block-container {{ 
        padding: 0 !important; 
        max-width: 100% !important; 
        background-color: #000000 !important;
    }}

    /* CUSTOM FIXED HEADER */
    .custom-header {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 70px;
        background: #111;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        z-index: 9999;
        border-bottom: 1px solid #333;
        box-sizing: border-box;
    }}

    .header-left {{ display: flex; align-items: center; gap: 15px; }}
    .header-right {{ display: flex; align-items: center; gap: 10px; }}

    /* TOUCH TARGETS (44x44px min) */
    .nav-btn, .ctrl-btn {{
        background: #222;
        color: white;
        border: 1px solid #444;
        border-radius: 6px;
        height: 44px;
        min-width: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: monospace;
        font-weight: bold;
        text-decoration: none;
        cursor: pointer;
    }}

    /* LÅTTEXT-AREA */
    .lyrics-content {{
        margin-top: 90px;
        padding: 20px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
        color: #efefef;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. VY-LOGIK: BIBLIOTEK ---
if st.session_state.page == "library":
    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True) # Spacer
    st.markdown("<h2 style='color:#666; padding-left:20px;'>BIBLIOTEK</h2>", unsafe_allow_html=True)
    
    songs = get_songs()
    for display_name, file_stem in songs.items():
        # Vi använder Streamlits standardknappar här för enkelhet i listan
        if st.button(display_name, key=file_stem, use_container_width=True):
            st.session_state.active_song = file_stem
            st.session_state.page = "lyrics"
            st.session_state.transpose = 0
            st.rerun()

# --- 5. VY-LOGIK: LÅTVY ---
elif st.session_state.page == "lyrics":
    # --- CUSTOM HTML HEADER ---
    # Vi använder st.write med HTML för att rendera kontrollerna fysiskt i headern
    header_html = f"""
    <div class="custom-header">
        <div class="header-left">
            {logo_tag}
        </div>
        <div class="header-right">
            <div id="btn-transpose-down" class="ctrl-btn"> - </div>
            <div id="btn-transpose-up" class="ctrl-btn"> + </div>
            <div id="btn-scroll" class="ctrl-btn" style="background:{'#D187FF' if st.session_state.scrolling else '#222'}; color:{'#000' if st.session_state.scrolling else '#fff'}"> 
                {'STOPP' if st.session_state.scrolling else 'SCROLL'} 
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Navigationsknapp (Streamlit-native men placeras under headern i koden)
    # För att få biblioteksknappen att sitta i headern använder vi en kolumn-hack
    # men vi placerar den i en "st.columns" precis under headern.
    col_nav, col_empty = st.columns([1, 2])
    with col_nav:
        st.markdown('<div style="position:fixed; top:13px; left:60px; z-index:10000;">', unsafe_allow_html=True)
        if st.button("⬅ BIBLIO", key="back_btn"):
            st.session_state.page = "library"
            st.session_state.scrolling = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Transponerings-hack (Dolda knappar som triggas av HTML-klick kan vara svårt i Streamlit, 
    # så vi kör Popover för inställningar precis som förut men placerar den i headern)
    st.markdown('<div style="position:fixed; top:13px; right:15px; z-index:10000;">', unsafe_allow_html=True)
    with st.popover("⚙️"):
        st.write(f"Tone: **{st.session_state.transpose}**")
        c1, c2 = st.columns(2)
        if c1.button("–"): st.session_state.transpose -= 1; st.rerun()
        if c2.button("+"): st.session_state.transpose += 1; st.rerun()
        st.session_state.scrolling = st.toggle("Autoscroll", value=st.session_state.scrolling)
        st.session_state.speed = st.slider("Fart", 1, 100, st.session_state.speed)
    st.markdown('</div>', unsafe_allow_html=True)

    # LÅTTEXT
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        
        lyrics_html = process_lyrics(raw_content, st.session_state.transpose)
        st.markdown(f'<div class="lyrics-content">{lyrics_html}</div>', unsafe_allow_html=True)

# --- 6. ROBUST SCROLL ENGINE (JAVASCRIPT) ---
if st.session_state.scrolling and st.session_state.page == "lyrics":
    delay = int(120 - st.session_state.speed)
    st.components.v1.html(f"""
        <script>
            function doScroll() {{
                window.parent.window.scrollBy({{
                    top: 1,
                    left: 0,
                    behavior: 'instant'
                }});
            }}
            if (window.parent.scrollTimer) clearInterval(window.parent.scrollTimer);
            window.parent.scrollTimer = setInterval(doScroll, {delay});
        </script>
    """, height=0)
else:
    st.components.v1.html("""
        <script>
            if (window.parent.scrollTimer) clearInterval(window.parent.scrollTimer);
        </script>
    """, height=0)
