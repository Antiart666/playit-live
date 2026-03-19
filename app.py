import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. SETUP ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state: st.session_state.page = "library"
if "active_song" not in st.session_state: st.session_state.active_song = None
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scrolling" not in st.session_state: st.session_state.scrolling = False
if "speed" not in st.session_state: st.session_state.speed = 30

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK ---
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

# --- 3. CSS (BRUTE FORCE LOGO & UI) ---
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="custom-logo">' if logo_b64 else '<b style="color:white;">PLAYIT!</b>'

st.markdown(f"""
<style>
    /* Dölj Streamlit UI helt */
    header, [data-testid="stHeader"], footer, [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{ background-color: #000 !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* HEADER */
    .app-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 90px;
        background: #111; z-index: 9998; border-bottom: 1px solid #333;
        display: flex; align-items: center; padding: 0 15px;
    }}

    /* PUNKT 1: TVINGAD LOGO-STORLEK */
    .custom-logo {{
        width: 150px !important; /* Exakt bredd enligt spec */
        height: auto;
        object-fit: contain;
    }}

    /* LYRICS (16px enligt tidigare önskemål) */
    .lyrics-box {{
        margin-top: 110px; padding: 20px; padding-bottom: 250px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 16px; line-height: 1.5; white-space: pre-wrap;
        color: #eee;
    }}

    /* FIXED NAVIGATION (HÖGER) */
    .fixed-nav {{
        position: fixed; top: 22px; right: 15px; z-index: 10000;
        display: flex; gap: 10px;
    }}

    /* KNAPPAR */
    .stButton > button {{
        background: #222 !important; color: #fff !important;
        border: 1px solid #444 !important; height: 46px !important;
        font-weight: bold !important;
    }}
</style>
<div class="app-header">
    {logo_html}
</div>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---

if st.session_state.page == "library":
    st.markdown('<div class="lyrics-box">', unsafe_allow_html=True)
    st.write("### REPERTOAR")
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=f"btn_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.page = "lyrics"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- PUNKT 2: ÄNDRING AV NAMN ("LÅTAR") ---
    st.markdown('<div class="fixed-nav">', unsafe_allow_html=True)
    c_back, c_pop = st.columns([2, 1])
    
    with c_back:
        if st.button("⬅ LÅTAR", key="back_to_list"): # Uppdaterat namn
            st.session_state.page = "library"
            st.session_state.scrolling = False
            st.rerun()
            
    with c_pop:
        with st.popover("⚙️"):
            st.write("### INSTÄLLNINGAR")
            st.write(f"Ton: **{st.session_state.transpose}**")
            t1, t2, t3 = st.columns(3)
            if t1.button("–"): st.session_state.transpose -= 1; st.rerun()
            if t2.button("STD"): st.session_state.transpose = 0; st.rerun()
            if t3.button("+"): st.session_state.transpose += 1; st.rerun()
            st.divider()
            st.session_state.scrolling = st.toggle("AUTOSCROLL", value=st.session_state.scrolling)
            st.session_state.speed = st.slider("FART", 1, 100, st.session_state.speed)
    st.markdown('</div>', unsafe_allow_html=True)

    # LÅTTEXT
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = process_lyrics(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="lyrics-box">{content}</div>', unsafe_allow_html=True)

# --- 5. PUNKT 3: REPARATION AV AUTOSCROLL (JS BRYGGA) ---
if st.session_state.scrolling and st.session_state.page == "lyrics":
    # Beräkna hastighet för mjukare rörelse
    # Högre fart i slidern = kortare intervall mellan 1px scroll
    ms_delay = max(5, int(100 - st.session_state.speed))
    
    st.components.v1.html(f"""
        <script>
            // Rensa gamla loopar för att undvika acceleration
            if (window.parent._activeScroll) {{
                clearInterval(window.parent._activeScroll);
            }}
            
            // window.parent når utanför iframen till huvudfönstret
            window.parent._activeScroll = setInterval(function() {{
                window.parent.window.scrollBy({{
                    top: 1,
                    left: 0,
                    behavior: 'auto' // 'auto' är ofta stabilare än 'smooth' i loopar
                }});
            }}, {ms_delay});
        </script>
    """, height=0)
else:
    st.components.v1.html("""
        <script>
            if (window.parent._activeScroll) {
                clearInterval(window.parent._activeScroll);
                window.parent._activeScroll = null;
            }
        </script>
    """, height=0)
