import streamlit as st
import re
import base64
from pathlib import Path

# --- 1. INITIAL CONFIG & SESSION STATE ---
st.set_page_config(
    page_title="PlayIt! Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initiera värden om de inte finns
for key, val in {
    "active_song": None, 
    "transpose": 0, 
    "scrolling": False, 
    "speed": 30
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

# --- 2. LOGIK & FUNKTIONER ---
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
    new_index = (notes.index(root) + steps) % 12
    return f"{notes[new_index]}{suffix}"

def process_content(text, steps):
    # Transponera ackord inuti []
    text = re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)
    # Färglägg ackord till lila/rosa
    return re.sub(r"\[(.*?)\]", r'<b style="color:#D187FF; font-weight:900;">[\1]</b>', text)

# --- 3. CSS-INJEKTION (TOTAL ÖVERSYN) ---
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:180px;">' if logo_b64 else '<h1 style="color:white;margin:0;">PLAYIT!</h1>'

st.markdown(f"""
<style>
    /* Dölj Streamlits standard-UI */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
    
    /* Maximera skärmytan */
    .main .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }}

    /* STICKY HEADER */
    .sticky-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #000000;
        z-index: 1000;
        border-bottom: 1px solid #333;
        padding: 10px 0;
    }}

    /* CENTRERING AV LOGO */
    .logo-box {{
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }}

    /* JUSTERING AV LÅTTEXT */
    .song-container {{
        margin-top: 180px; /* Tillräckligt för att gå fritt från headern */
        padding: 20px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
        color: #efefef;
    }}

    /* STYLING AV KNAPPAR INUTI HEADER */
    .stButton > button {{
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 5px !important;
        width: 100%;
        height: 38px;
    }}
    
    /* Speciell styling för ON/OFF-knappen */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] .stButton > button[kind="primary"] {{
        background-color: #D187FF !important;
        color: black !important;
        font-weight: bold;
    }}

</style>

<div class="sticky-header">
    <div class="logo-box">
        {logo_html}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. HEADER-KONTROLLER (RAD 1 & 2) ---
# Vi placerar kontrollerna i en container som vi placerar "ovanpå" den fixerade headern visuellt
header_placeholder = st.empty()

with header_placeholder.container():
    # En osynlig spacer för att knuffa ner knapparna under loggan men inuti den fixerade headern
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    
    if st.session_state.active_song:
        # RAD 1: Navigering
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅ LÅTAR"):
                st.session_state.active_song = None
                st.session_state.scrolling = False
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align:center; color:#666; margin:0;'>{st.session_state.active_song.replace('_',' ')}</p>", unsafe_allow_html=True)
        
        # RAD 2: Kontroller
        # Vi använder 6 kolumner för att få plats på en mobilrad
        ctrl = st.columns([1, 1, 1, 2, 1, 1])
        with ctrl[0]:
            if st.button("–"): 
                st.session_state.transpose -= 1
                st.rerun()
        with ctrl[1]:
            if st.button("STD"): 
                st.session_state.transpose = 0
                st.rerun()
        with ctrl[2]:
            if st.button("+"): 
                st.session_state.transpose += 1
                st.rerun()
        with ctrl[3]:
            btn_label = "⏸ STOPP" if st.session_state.scrolling else "▶ SCROLL"
            if st.button(btn_label, type="primary"):
                st.session_state.scrolling = not st.session_state.scrolling
                st.rerun()
        with ctrl[4]:
            if st.button("S-"):
                st.session_state.speed = max(5, st.session_state.speed - 5)
        with ctrl[5]:
            if st.button("S+"):
                st.session_state.speed = min(100, st.session_state.speed + 5)

# --- 5. HUVUDINNEHÅLL (VÄXLA VY) ---
if not st.session_state.active_song:
    # --- VY: LÅTLISTA ---
    st.markdown('<div class="song-container">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>REPERTOAR</h2>", unsafe_allow_html=True)
    songs = get_songs()
    for display_name, file_stem in songs.items():
        if st.button(display_name, key=file_stem, use_container_width=True):
            st.session_state.active_song = file_stem
            st.session_state.transpose = 0
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- VY: SPEL-LÄGE ---
    file_path = LIB_DIR / f"{st.session_state.active_song}.md"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        processed_text = process_content(content, st.session_state.transpose)
        
        st.markdown(f"""
        <div class="song-container">
            {processed_text}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Filen saknas.")

# --- 6. JAVASCRIPT SCROLL-MOTOR ---
if st.session_state.scrolling:
    # Beräkna hastighet (delay i ms). 
    # Streamlit speed 100 = snabb (låg delay), 5 = långsam (hög delay)
    scroll_delay = int(105 - st.session_state.speed)
    
    st.components.v1.html(f"""
        <script>
            function smoothScroll() {{
                window.parent.window.scrollBy(0, 1);
            }}
            if (window.parent.scrollInterval) {{
                clearInterval(window.parent.scrollInterval);
            }}
            window.parent.scrollInterval = setInterval(smoothScroll, {scroll_delay});
        </script>
    """, height=0)
else:
    st.components.v1.html("""
        <script>
            if (window.parent.scrollInterval) {
                clearInterval(window.parent.scrollInterval);
            }
        </script>
    """, height=0)
