import streamlit as st
import os
import re
import base64

# 1. Konfiguration
st.set_page_config(
    page_title="PlayIt Live",
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
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def transpose_chords(text, steps):
    if steps == 0: return text
    chords = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    def replace_chord(match):
        chord = match.group(0)
        base = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base):]
        norm = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base in norm: base = norm[base]
        if base in chords:
            new_idx = (chords.index(base) + steps) % 12
            return chords[new_idx] + suffix
        return chord
    return re.sub(r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b", replace_chord, text)

# --- CSS (Stabil layout utan krockar) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* Tvinga ljust tema */
    header, footer {{ visibility: hidden !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* Global text */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif; }}

    /* Fixerad Logga/Hemknapp */
    .logo-container {{
        position: fixed;
        top: 10px;
        left: 15px;
        z-index: 999;
        transform: rotate(-8deg);
    }}
    .logo-img {{
        width: 75px;
        border: 2px solid #000;
        border-radius: 12px;
        background: #000;
    }}

    /* Läsrutan */
    .song-box {{
        height: 85vh;
        overflow-y: auto;
        background: #ffffff;
        border: 3px solid #000;
        border-radius: 30px;
        padding: 20px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px;
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 10px;
    }}

    /* Knappar (Vita med svarta kanter) */
    .stButton>button {{
        background: #ffffff !important;
        color: #000 !important;
        border: 2px solid #000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        width: 100%;
    }}

    /* Justering för att inget ska hamna under loggan */
    .main-content {{
        margin-top: 60px;
    }}
    
    .settings-card {{
        background: #f9f9f9;
        border: 2px dashed #000;
        border-radius: 25px;
        padding: 20px;
        margin-top: 40px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "speed" not in st.session_state: st.session_state.speed = 0

# Loggan som Hem-knapp (nu som en rad i Streamlit för stabilitet)
col_logo, col_filler = st.columns([1, 4])
with col_logo:
    if st.button("🏠 HEM", key="home_btn"):
        st.session_state.view = "list"
        st.rerun()

# Rita loggan visuellt
if logo_b64:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" class="logo-img"></div>', unsafe_allow_html=True)

songs_dir = "library"

# --- RENDERER ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte.")
else:
    if st.session_state.view == "list":
        # --- ARKIV ---
        st.subheader("Mina Låtar")
        
        for root, dirs, files in os.walk(songs_dir):
            cat = os.path.basename(root)
            if cat == "library": cat = "Alla"
            
            valid = sorted([f for f in files if f.endswith(".md")])
            if valid:
                st.write(f"**{cat.upper()}**")
                cols = st.columns(2)
                for idx, f in enumerate(valid):
                    with cols[idx % 2]:
                        if st.button(clean_title(f), key=os.path.join(root, f)):
                            st.session_state.song_path = os.path.join(root, f)
                            st.session_state.view = "song"
                            st.rerun()
        
        # --- INSTÄLLNINGAR LÄNGST NER ---
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        st.write("### ⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            tc1, tc2 = st.columns(2)
            if tc1.button("-", key="t_m"): st.session_state.transpose -= 1
            if tc2.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            sc1, sc2 = st.columns(2)
            if sc1.button("Sakta", key="s_m"): st.session_state.speed = max(0, st.session_state.speed - 1)
            if sc2.button("Fort", key="s_p"): st.session_state.speed = min(10, st.session_state.speed + 1)
            st.write(f"Fart: {st.session_state.speed}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SCENLÄGE ---
        # Enkel "Tillbaka"-knapp istället för krångligt dubbelklick
        if st.button("← TILLBAKA TILL LISTAN"):
            st.session_state.view = "list"
            st.rerun()
            
        with open(st.session_state.song_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = transpose_chords(content, st.session_state.transpose)
        display_text = content + ("\n" * 50)

        # SCROLL-LOGIK (Utan window.parent för att undvika Script Error)
        if st.session_state.speed > 0:
            delay = (11 - st.session_state.speed) * 40
            st.markdown(f"""
                <script>
                var el = document.getElementById("song-rutan");
                if (window.scroller) clearInterval(window.scroller);
                window.scroller = setInterval(function() {{
                    if (el) el.scrollTop += 1;
                }}, {delay});
                </script>
            """, unsafe_allow_html=True)

        st.markdown(f'<div id="song-rutan" class="song-box">{display_text}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
