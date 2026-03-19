import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. SETUP ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

# Session State för att hålla koll på appens läge
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

# --- 3. CSS (FÖRÄNDRAD FÖR ATT STYLA SWITCHN) ---
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">' if logo_b64 else '<b style="color:white;font-size:30px;">PLAYIT!</b>'

st.markdown(f"""
<style>
    /* Dölj Streamlits standard-element */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ 
        display: none !important; 
    }}
    
    [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* HEADERN */
    .custom-header {{
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 180px;
        background: #000; 
        z-index: 999; 
        border-bottom: 1px solid #222;
        display: flex; 
        justify-content: space-between;
        align-items: center; 
        padding: 0 20px;
    }}
    
    .stage-logo {{ 
        height: 140px; 
        width: auto; 
        object-fit: contain;
    }}

    /* LYRICS (18px master size) */
    .lyrics-wrapper {{
        margin-top: 200px; 
        padding: 20px; 
        padding-bottom: 150px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; 
        line-height: 1.5; 
        white-space: pre-wrap;
        color: #efefef;
    }}

    /* KNAPPAR & TOGGLE */
    .stButton > button {{
        background: #111 !important; 
        color: #fff !important;
        border: 1px solid #444 !important; 
        height: 60px !important;
        padding: 0 25px !important;
        font-weight: bold !important;
    }}

    /* Gör switchen lila när den är på */
    div[data-testid="stWidgetLabel"] {{ color: white !important; font-weight: bold !important; }}
    .st-bc {{ background-color: #D187FF !important; }} 
</style>

<div class="custom-header">
    {logo_html}
</div>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION & SIDOR ---

if st.session_state.page == "list":
    st.markdown('<div class="lyrics-wrapper">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#444;'>BIBLIOTEK</h2>", unsafe_allow_html=True)
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=f"list_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.page = "lyrics"
            st.session_state.transpose = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- HEADER-KNAPPAR ---
    with st.container():
        # Placering av Settings och Låtar-knapp
        cols = st.columns([5.5, 1.5, 3]) 
        
        with cols[1]:
            st.markdown('<div style="margin-top:60px;"></div>', unsafe_allow_html=True)
            with st.popover("⚙️"):
                st.write("### Inställningar")
                
                # Transponering
                st.write(f"Tone: **{st.session_state.transpose}**")
                t_c1, t_c2 = st.columns(2)
                if t_c1.button("–"): st.session_state.transpose -= 1; st.rerun()
                if t_c2.button("+"): st.session_state.transpose += 1; st.rerun()
                
                st.divider()
                
                # SCROLL SWITCH (Här är förändringen)
                st.session_state.scrolling = st.toggle("AUTOSCROLL", value=st.session_state.scrolling)
                
                # Fart-slider
                st.session_state.speed = st.slider("Hastighet", 1, 100, st.session_state.speed)
                
        with cols[2]:
            st.markdown('<div style="margin-top:60px;"></div>', unsafe_allow_html=True)
            if st.button("⬅ LÅTAR", key="nav_list_btn", use_container_width=True):
                st.session_state.page = "list"
                st.session_state.scrolling = False
                st.rerun()

    # RENDER TEXT
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = process_content(f.read(), st.session_state.transpose)
        st.markdown(f'<div class="lyrics-wrapper">{content}</div>', unsafe_allow_html=True)

# --- 5. SCROLL ENGINE (Javascript) ---
if st.session_state.scrolling:
    # Delay beräknas så att högre siffra i slidern = snabbare scroll
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
    st.components.v1.html("<script>if(window.parent.scrollInt) clearInterval(window.parent.scrollInt);</script>", height=0)
