import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Maximerad yta och ren layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER ---

def clean_title(filename):
    """Gör filnamn som LÅT_NAMN.md till Låt namn"""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert för inbäddning"""
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

# --- DESIGN (Logga vänster, LÅTAR-knapp höger, båda med skugga) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STANDARD-ELEMENT FRÅN STREAMLIT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXTSTIL */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }}

    /* LOGGAN (Uppe till vänster, lutar -8 grader, med skugga) */
    .nav-logo-fixed-left {{
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        width: 110px !important;
        height: auto !important;
        z-index: 999999 !important;
        transform: rotate(-8deg) !important;
        filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.3)); /* Skugga på loggan */
        pointer-events: none;
    }}

    /* LÅTAR-KNAPPEN (Uppe till höger, med skugga) */
    div[data-testid="stButton"] > button[key="main_nav_btn"] {{
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        width: 140px !important;
        height: 60px !important;
        z-index: 1000000 !important;
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        color: #000000 !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
        /* Dubbel skugga för både djup och tydlighet */
        box-shadow: 4px 4px 10px rgba(0,0,0,0.2), 4px 4px 0px #000000 !important;
    }}

    /* MELLANRUM FÖR ATT UNDVIKA ATT LISTAN HAMNAR BAKOM HEADER */
    .top-margin-barrier {{
        height: 110px;
        display: block;
    }}

    /* LÄSRUTAN (GRÄNSLÖS & TABS-VÄNLIG) */
    .song-reader-area {{
        height: 92vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 5px !important;
        border: none !important; /* Ingen ram runt texten */
        
        /* Monospace (Courier) för perfekta tabs */
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important; 
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
    }}

    /* ARKIV-KNAPPAR I LISTAN */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}

    /* VERKTYGSBOX LÄNGST NER */
    .settings-tray {{
        margin: 40px 10px;
        padding: 25px;
        background-color: #fcfcfc;
        border: 2px dashed #000;
        border-radius: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK & STATE ---
if "view" not in st.session_state: st.session_state.view = "list"
if "current_song_path" not in st.session_state: st.session_state.current_song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll_speed" not in st.session_state: st.session_state.scroll_speed = 0

# RITA LOGGAN (Vänster)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo-fixed-left">', unsafe_allow_html=True)
else:
    st.markdown('<div class="nav-logo-fixed-left" style="font-weight:900;">LOGO</div>', unsafe_allow_html=True)

# RITA NAV-KNAPPEN (Höger)
if st.button("LÅTAR", key="main_nav_btn"):
    st.session_state.view = "list"
    st.session_state.current_song_path = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte. Kontrollera din GitHub-struktur.")
else:
    if st.session_state.view == "list":
        # ARKIVVYN
        st.markdown('<div class="top-margin-barrier"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, f in enumerate(valid_files):
                    with cols[i % 2]:
                        full_path = os.path.join(root, f)
                        if st.button(clean_title(f), key=full_path):
                            st.session_state.current_song_path = full_path
                            st.session_state.view = "song"
                            st.rerun()

        # VERKTYGSPANEL
        st.markdown('<div class="settings-tray">', unsafe_allow_html=True)
        st.subheader("⚙️ Verktyg")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            t1, t2 = st.columns(2)
            if t1.button("-", key="t_m"): st.session_state.transpose -= 1
            if t2.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            s1, s2 = st.columns(2)
            if s1.button("Sakta", key="s_m"): st.session_state.scroll_speed = max(0, st.session_state.scroll_speed - 1)
            if s2.button("Fort", key="s_p"): st.session_state.scroll_speed = min(10, st.session_state.scroll_speed + 1)
            st.write(f"Fart: {st.session_state.scroll_speed}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # SCENVYN (Låten)
        # Sänker rutan något så att de flytande knapparna inte skymmer första raden
        st.markdown('<div style="height:75px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.current_song_path):
            with open(st.session_state.current_song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose)
            full_text = content + ("\n" * 65)

            # Auto-scroll-skript
            if st.session_state.scroll_speed > 0:
                delay = (11 - st.session_state.scroll_speed) * 45
                st.markdown(f"""
                    <script>
                    var box = document.getElementById("song-view");
                    if (window.playitScroll) clearInterval(window.playitScroll);
                    window.playitScroll = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {delay});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="song-reader-area">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
