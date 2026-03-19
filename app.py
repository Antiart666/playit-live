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

# --- 3. CSS (DEN STORA LAYOUT-FIXEN) ---
logo_b64 = get_logo_b64()
# Här tvingar vi in loggan med en fast höjd på 180px
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">' if logo_b64 else '<b style="color:white;font-size:40px;">PLAYIT!</b>'

st.markdown(f"""
<style>
    /* DÖDA STREAMLITS EGNA ELEMENT HELT */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ 
        display: none !important; 
        height: 0 !important;
        opacity: 0 !important;
    }}
    
    [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* VÅR NYA SUPER-HEADER (Z-INDEX ÄR NYCKELN) */
    .custom-header {{
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 200px; /* Mycket högre för att rymma loggan */
        background: #000; 
        z-index: 9999999; /* Ligger över allt annat */
        border-bottom: 1px solid #222;
        display: flex; 
        align-items: center; 
        padding: 0 30px;
    }}
    
    .stage-logo {{ 
        height: 180px; /* REJÄL STORLEK */
        width: auto; 
        object-fit: contain;
        margin-right: 40px;
    }}

    /* LYRICS AREA - MÅSTE BÖRJA LÄGRE NER NU */
    .lyrics-wrapper {{
        margin-top: 220px; 
        padding: 30px; 
        padding-bottom: 150px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 24px; /* Lite större text för scenen */
        line-height: 1.6; 
        white-space: pre-wrap;
        color: #f0f0f0;
    }}

    /* KNAPPARNA I HEADERN */
    .stButton > button {{
        background: #1a1a1a !important; 
        color: #fff !important;
        border: 1px solid #444 !important; 
        height: 50px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }}
</style>
<div class="custom-header">{logo_html}</div>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---

if st.session_state.page == "list":
    st.markdown('<div class="lyrics-wrapper">', unsafe_allow_html=True)
    st.markdown("<h1 style='color:#444; margin-bottom:40px;'>REPERTOAR</h1>", unsafe_allow_html=True)
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=f"s_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.page = "lyrics"
            st.session_state.transpose = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # LÅTVY - KONTROLLER I HEADERN
    # Vi lägger knapparna i Streamlit-kolumner som vi visuellt "flyttar upp" i headern
    header_cols = st.columns([2.5, 4, 1])
    
    with header_cols[0]:
        st.markdown('<div style="margin-top:75px;"></div>', unsafe_allow_html=True)
        if st.button("⬅ TILL LISTAN"):
            st.session_state.page = "list"
            st.session_state.scrolling = False
            st.rerun()
            
    with header_cols[1]:
        # Visar låtnamn diskret
        st.markdown(f"<p style='text-align:center; line-height:200px; margin:0; color:#333; font-weight:bold; font-size:20px;'>{st.session_state.active_song.replace('_',' ')}</p>", unsafe_allow_html=True)
        
    with header_cols[2]:
        st.markdown('<div style="margin-top:75px;"></div>', unsafe_allow_html=True)
        with st.popover("⚙️"):
            st.write("### Inställningar")
            st.write(f"Tone: **{st.session_state.transpose}**")
            t_col1, t_col2 = st.columns(2)
            if t_col1.button("–"): st.session_state.transpose -= 1; st.rerun()
            if t_col2.button("+"): st.session_state.transpose += 1; st.rerun()
            st.divider()
            st.session_state.speed = st.slider("Fart", 1, 100, st.session_state.speed)
            if st.button("START/STOPP SCROLL", type="primary", use_container_width=True):
                st.session_state.scrolling = not st.session_state.scrolling
                st.rerun()

    # RENDER LÅTTEXT
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = process_content(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="lyrics-wrapper">{content}</div>', unsafe_allow_html=True)

# --- 5. SCROLL ENGINE ---
if st.session_state.scrolling:
    delay = int(115 - st.session_state.speed)
    st.components.v1.html(f"""
        <script>
            if (window.parent.si) clearInterval(window.parent.si);
            window.parent.si = setInterval(() => {{
                window.parent.window.scrollBy(0, 1);
            }}, {delay});
        </script>
    """, height=0)
else:
    st.components.v1.html("<script>clearInterval(window.parent.si);</script>", height=0)
