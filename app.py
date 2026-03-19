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
if "speed" not in st.session_state: st.session_state.speed = 35

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK ---
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
    return re.sub(r"\[(.*?)\]", r'<b style="color:#D187FF; font-weight:900;">[\1]</b>', text)

# --- 3. CSS (MED MASTER-PROMPT TEXTSTORLEK) ---
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">' if logo_b64 else '<b style="color:white;font-size:30px;">PLAYIT!</b>'

st.markdown(f"""
<style>
    /* Total rensning av Streamlit-skräp */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ 
        display: none !important; 
        height: 0 !important;
    }}
    
    [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* FIXERAD HEADER */
    .custom-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 180px;
        background: #000; z-index: 99999; border-bottom: 1px solid #222;
        display: flex; align-items: center; padding: 0 20px;
    }}
    
    .stage-logo {{ 
        height: 150px; width: auto; object-fit: contain; margin-right: 20px;
    }}

    /* LYRICS - MASTER SETTINGS (18px font) */
    .lyrics-wrapper {{
        margin-top: 190px; 
        padding: 20px; 
        padding-bottom: 150px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; /* TILLBAKA TILL OPTIMAL STORLEK */
        line-height: 1.5; 
        white-space: pre-wrap;
        color: #efefef;
    }}

    /* KNAPPAR */
    .stButton > button {{
        background: #111 !important; color: #fff !important;
        border: 1px solid #333 !important; height: 45px !important;
        font-weight: bold !important;
    }}
</style>
<div class="custom-header">{logo_html}</div>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---

if st.session_state.page == "list":
    st.markdown('<div class="lyrics-wrapper">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#444;'>BIBLIOTEK</h2>", unsafe_allow_html=True)
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=f"btn_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.page = "lyrics"
            st.session_state.transpose = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # KONTROLLER I HEADERN (Flyttade för att matcha loggan)
    h_col1, h_col2, h_col3 = st.columns([2, 4, 1])
    
    with h_col1:
        st.markdown('<div style="margin-top:65px;"></div>', unsafe_allow_html=True)
        if st.button("⬅ LÅTAR"):
            st.session_state.page = "list"
            st.session_state.scrolling = False
            st.rerun()
            
    with h_col2:
        # Låtnamn diskret i headern
        st.markdown(f"<p style='text-align:center; line-height:180px; margin:0; color:#333; font-weight:bold;'>{st.session_state.active_song.replace('_',' ')}</p>", unsafe_allow_html=True)
        
    with h_col3:
        st.markdown('<div style="margin-top:65px;"></div>', unsafe_allow_html=True)
        with st.popover("⚙️"):
            st.write("### Panel")
            st.write(f"Tone: **{st.session_state.transpose}**")
            t_c1, t_c2 = st.columns(2)
            if t_c1.button("–"): st.session_state.transpose -= 1; st.rerun()
            if t_c2.button("+"): st.session_state.transpose += 1; st.rerun()
            st.divider()
            st.session_state.speed = st.slider("Fart", 1, 100, st.session_state.speed)
            if st.button("SCROLL PÅ/AV", type="primary", use_container_width=True):
                st.session_state.scrolling = not st.session_state.scrolling
                st.rerun()

    # RENDER
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = process_content(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="lyrics-wrapper">{content}</div>', unsafe_allow_html=True)

# --- 5. SCROLL ---
if st.session_state.scrolling:
    delay = int(115 - st.session_state.speed)
    st.components.v1.html(f"""
        <script>
            if (window.parent.scrollInt) clearInterval(window.parent.scrollInt);
            window.parent.scrollInt = setInterval(() => {{
                window.parent.window.scrollBy(0, 1);
            }}, {delay});
        </script>
    """, height=0)
else:
    st.components.v1.html("<script>clearInterval(window.parent.scrollInt);</script>", height=0)
