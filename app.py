import streamlit as st
import os
import re
import base64

# 1. Grundinställningar - Tvinga fram ljus layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    if steps == 0: return text
    def replace_chord(match):
        chord = match.group(0)
        base_chord = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base_chord):]
        norm_map = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base_chord in norm_map: base_chord = norm_map[base_chord]
        if base_chord in CHORDS:
            new_index = (CHORDS.index(base_chord) + steps) % 12
            return CHORDS[new_index] + suffix
        return chord
    return re.sub(r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b", replace_chord, text)

# --- DESIGN (Stabiliserad för Mobil) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* TVINGA VITT TEMA OCH DÖLJ ALLT SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GÖR ALL TEXT SVART */
    h1, h2, h3, p, span, div, label, li, button {{ 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important; 
    }}

    /* HUVUDYTA */
    .block-container {{
        padding-top: 1rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* LOGGA-KNAPPEN (HELT NY METOD) */
    div[data-testid="stButton"] > button[key="logo_home"] {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        width: 130px !important; /* Storlek på din logga */
        height: 70px !important;
        z-index: 99999 !important;
        background-image: url("data:image/png;base64,{logo_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
    }}

    /* STOPPA KAOS: MELLANRUM HÖGST UPP */
    .app-spacer {{
        height: 100px;
        width: 100%;
        display: block;
    }}

    /* LÄSRUTAN */
    .song-view {{
        height: 88vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 20px;
        border: 3px solid #000000;
        border-radius: 30px; 
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 5px;
    }}

    /* ARKIV-KNAPPAR */
    .stButton > button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 18px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
    }}

    /* VERKTYGS-BOX */
    .tools-footer {{
        margin-top: 50px;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 25px;
        border: 2px dashed #000000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State & Navigation
if "view" not in st.session_state: st.session_state.view = "list"
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- LOGGAN SOM KNAPP ---
# Vi lägger denna först. Den blir osynlig men visar din bild via CSS.
if st.button(" ", key="logo_home"):
    st.session_state.view = "list"
    st.rerun()

# Spacer för att trycka ner resten av innehållet under loggan
st.markdown('<div class="app-spacer"></div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. Logik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.header("Arkiv")
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            if valid_songs:
                st.markdown(f'<div style="font-weight:900; color:#666; margin-top:15px; font-size:12px;">{category.upper()}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.current_path = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # VERKTYG
        st.markdown('<div class="tools-footer">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            t_m, t_p = st.columns(2)
            if t_m.button("-", key="t_m"): st.session_state.transpose -= 1
            if t_p.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            s_m, s_p = st.columns(2)
            if s_m.button("Sakta", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s_p.button("Fort", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET ---
        # Back-knapp (visas endast vid dubbelklick)
        if st.button("← ARKIV", key="manual_back"):
            st.session_state.view = "list"
            st.rerun()

        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        display_text = transpose_chords(raw_text, st.session_state.transpose)
        display_text += ("\n" * 50)

        # JavaScript för Dubbelklick & Scroll (Säkrad för mobiler utan window.parent)
        st.markdown(f"""
            <script>
            // Hitta tillbaka-knappen
            var btns = document.querySelectorAll('button');
            var backBtn = Array.from(btns).find(b => b.innerText.includes("ARKIV"));
            if (backBtn) {{
                var btnContainer = backBtn.parentElement.parentElement.parentElement;
                btnContainer.style.display = 'none';
                
                document.addEventListener('dblclick', function() {{
                    btnContainer.style.display = (btnContainer.style.display === 'none') ? 'block' : 'none';
                }});
            }}

            // Scroll
            var box = document.getElementById("song-container-id");
            if (window.playitScroll) clearInterval(window.playitScroll);
            if ({st.session_state.scroll} > 0) {{
                var speed = (11 - {st.session_state.scroll}) * 40;
                window.playitScroll = setInterval(function() {{ if (box) box.scrollTop += 1; }}, speed);
            }}
            </script>
        """, unsafe_allow_html=True)

        st.markdown(f'<div id="song-container-id" class="song-view">{display_text}</div>', unsafe_allow_html=True)
