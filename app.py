import streamlit as st
import os
import re
import base64

# 1. Konfiguration
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER ---

def clean_title(filename):
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    if steps == 0: return text
    def replace_chord(match):
        chord = match.group(0)
        base = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base):]
        norm = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base in norm: base = norm[base]
        if base in CHORDS:
            idx = (CHORDS.index(base) + steps) % 12
            return CHORDS[idx] + suffix
        return chord
    return re.sub(r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b", replace_chord, text)

# --- CSS (Den kompromisslösa versionen) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT STANDARD-SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXT */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
    }}

    /* LOGGAN / HEMKNAPPEN (Dödar all spilltext) */
    div[data-testid="stButton"] > button[key="logo_home"] {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        width: 120px !important; 
        height: 80px !important;
        z-index: 1000000 !important;
        
        /* Bilden */
        background-image: url("data:image/png;base64,{logo_b64 if logo_b64 else ''}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        
        /* Dölj ALL text och ikoner inuti knappen */
        border: none !important;
        box-shadow: none !important;
        color: transparent !important;
        font-size: 0px !important;
        line-height: 0 !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
    }}
    
    /* Targetar p-taggen inuti knappen som Streamlit ofta använder */
    div[data-testid="stButton"] > button[key="logo_home"] p {{
        display: none !important;
    }}

    div[data-testid="stButton"] > button[key="logo_home"]:active {{
        transform: rotate(-8deg) scale(0.9) !important;
    }}

    /* STOPPA BOKSTAVSKAOSET */
    .spacer {{ height: 115px; display: block; }}

    /* LÄSRUTAN (MAXAD) */
    .song-stage-final {{
        height: 92vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        border: 4px solid #000000;
        border-radius: 35px; 
        padding: 25px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; 
        line-height: 1.4;
        white-space: pre-wrap;
        margin-top: 10px;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 18px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
    }}

    /* VERKTYGSBOX */
    .tools-tray {{
        margin-top: 40px;
        padding: 25px;
        background-color: #f9f9f9;
        border: 2px dashed #000;
        border-radius: 25px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song" not in st.session_state: st.session_state.song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# DEN ENDA KNAPPEN (Loggan)
if st.button(" ", key="logo_home"):
    st.session_state.view = "list"
    st.session_state.song = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # ARKIV
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, f in enumerate(valid_files):
                    with cols[i % 2]:
                        if st.button(clean_title(f), key=os.path.join(root, f)):
                            st.session_state.song = os.path.join(root, f)
                            st.session_state.view = "song"
                            st.rerun()

        # VERKTYG
        st.markdown('<div class="tools-tray">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            if st.button("-", key="t_m"): st.session_state.transpose -= 1
            if st.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            if st.button("Sakta", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if st.button("Fort", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # SCEN (Låten)
        # Sänker rutan lite så loggan inte krockar med texten
        st.markdown('<div style="height:70px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song):
            with open(st.session_state.song, "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose)
            full_text = content + ("\n" * 55)

            # Auto-scroll
            if st.session_state.scroll > 0:
                speed = (11 - st.session_state.scroll) * 45
                st.markdown(f"""
                    <script>
                    var box = document.getElementById("song-view");
                    if (window.scroller) clearInterval(window.scroller);
                    window.scroller = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {speed});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="song-stage-final">{full_text}</div>', unsafe_allow_html=True)
