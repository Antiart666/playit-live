import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. SETUP ---
st.set_page_config(page_title="PlayIt! Pro", layout="wide", initial_sidebar_state="collapsed")

# Session State för navigering och inställningar
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
    # Transponera ackord [Am]
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    # Färga ackord lila/rosa för scenen
    return re.sub(r"\[(.*?)\]", r'<b style="color:#D187FF; font-weight:900;">[\1]</b>', text)

# --- 3. CSS (BLACK STAGE UI + LOGO 125% BOOST) ---
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="top-logo">' if logo_b64 else '<b class="top-logo-txt">PLAYIT!</b>'

st.markdown(f"""
<style>
    /* Svart bakgrund och nollställning av Streamlit */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    .main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* FIXED HEADER */
    .nav-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 90px;
        background: #111; z-index: 9999; border-bottom: 1px solid #333;
        display: flex; align-items: center; padding: 0 20px;
    }}
    /* LOGO ÖKAD 125% (Nu 80px hög) */
    .top-logo {{ height: 80px; width: auto; margin-right: 20px; }}
    .top-logo-txt {{ font-size: 28px; color: white; font-weight: 900; }}

    /* LYRICS AREA */
    .lyrics-box {{
        margin-top: 110px; padding: 25px; padding-bottom: 120px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 22px; line-height: 1.6; white-space: pre-wrap;
        color: #efefef; background: #000;
    }}

    /* KNAPPAR */
    .stButton > button {{
        background: #1a1a1a !important; color: #fff !important;
        border: 1px solid #444 !important; border-radius: 8px !important;
        font-weight: bold !important;
    }}
    button[kind="primary"] {{ background: #D187FF !important; color: #000 !important; border: none !important; }}
</style>
<div class="nav-header">{logo_html}</div>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION & SIDOR ---

if st.session_state.page == "list":
    st.markdown('<div class="lyrics-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#666;'>REPERTOAR</h2>", unsafe_allow_html=True)
    songs = get_songs()
    for name, stem in songs.items():
        if st.button(name, key=f"select_{stem}", use_container_width=True):
            st.session_state.active_song = stem
            st.session_state.page = "lyrics"
            st.session_state.transpose = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # LÅTVY - HEADER KONTROLLER (Sitter i sticky header-området)
    # Vi använder columns för att placera knapparna snyggt brevid loggan
    c_back, c_title, c_settings = st.columns([2, 4, 1])
    
    with c_back:
        st.markdown('<div style="margin-top:25px;"></div>', unsafe_allow_html=True)
        if st.button("⬅ LÅTAR"):
            st.session_state.page = "list"
            st.session_state.scrolling = False
            st.rerun()
            
    with c_title:
        # Visar låtnamn diskret i mitten
        st.markdown(f"<p style='text-align:center; line-height:90px; margin:0; color:#444; font-weight:bold;'>{st.session_state.active_song.replace('_',' ')}</p>", unsafe_allow_html=True)
        
    with c_settings:
        st.markdown('<div style="margin-top:25px;"></div>', unsafe_allow_html=True)
        with st.popover("⚙️"):
            st.write("### Inställningar")
            st.write(f"Ton: **{st.session_state.transpose}**")
            t1, t2, t3 = st.columns(3)
            if t1.button("–"): st.session_state.transpose -= 1; st.rerun()
            if t2.button("0"): st.session_state.transpose = 0; st.rerun()
            if t3.button("+"): st.session_state.transpose += 1; st.rerun()
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
        st.markdown(f'<div class="lyrics-box">{content}</div>', unsafe_allow_html=True)
    else:
        st.error("Filen hittades inte.")

# --- 5. SCROLL ENGINE (SÄKER MOT SCRIPT ERROR) ---
if st.session_state.scrolling:
    delay = int(110 - st.session_state.speed)
    st.components.v1.html(f"""
        <script>
        try {{
            const win = window.parent;
            if (win.scrollInterval) {{ clearInterval(win.scrollInterval); }}
            win.scrollInterval = setInterval(() => {{
                win.window.scrollBy({{top: 1, left: 0, behavior: 'instant'}});
            }}, {delay});
        }} catch (e) {{
            console.error("Scroll error:", e);
        }}
        </script>
    """, height=0)
else:
    st.components.v1.html("""
        <script>
        try {{
            const win = window.parent;
            if (win.scrollInterval) {{ clearInterval(win.scrollInterval); }}
        }} catch (e) {{}}
        </script>
    """, height=0)
