import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Tvinga fram en ren och stabil layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Gör filnamn till snygg text."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert. Returnerar None om filen saknas istället för att krascha."""
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return None
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

# --- DESIGN (Inter-font, Stabil layout och Rundade hörn) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STREAMLIT STANDARD-ELEMENT */
    header, footer, #MainMenu {{ visibility: hidden !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXTSTIL */
    * {{ 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        text-transform: none !important;
    }}

    .block-container {{
        padding-top: 1rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* ANIMATION: SVÄVANDE (FLOATING) */
    @keyframes floating {{
        0% {{ transform: rotate(-8deg) translateY(0px); }}
        50% {{ transform: rotate(-8deg) translateY(-5px); }}
        100% {{ transform: rotate(-8deg) translateY(0px); }}
    }}

    /* LOGGAN SOM HEMKNAPP MED ANIMATION OCH REAKTION */
    div[data-testid="stButton"] > button[key="logo_home_btn"] {{
        position: fixed !important;
        top: 15px !important;
        left: 20px !important;
        width: 110px !important;
        height: 65px !important;
        z-index: 99999 !important;
        
        background-image: {f'url("data:image/png;base64,{logo_b64}")' if logo_b64 else 'none'} !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: { 'transparent' if logo_b64 else '#000' } !important;
        
        border: none !important;
        color: { 'transparent' if logo_b64 else '#fff' } !important;
        box-shadow: none !important;
        cursor: pointer !important;
        
        animation: floating 3s ease-in-out infinite !important;
        transition: transform 0.1s ease-in-out !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        border-radius: 12px;
    }}
    
    div[data-testid="stButton"] > button[key="logo_home_btn"]:active {{
        transform: rotate(-8deg) scale(0.9) !important;
        animation: none !important;
    }}

    /* MELLANRUM HÖGST UPP */
    .app-top-spacer {{
        height: 90px;
        width: 100%;
        display: block;
    }}

    /* LÄSRUTAN (MAXIMERAD) */
    .song-display-area {{
        height: 88vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px;
        border: 3px solid #000000;
        border-radius: 35px; 
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 18px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}

    /* VERKTYGSPANEL */
    .bottom-tools {{
        margin-top: 40px;
        padding: 25px;
        background-color: #fcfcfc;
        border-radius: 30px;
        border: 2px dashed #000000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State Management
if "view" not in st.session_state: st.session_state.view = "list"
if "current_song_path" not in st.session_state: st.session_state.current_song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll_speed" not in st.session_state: st.session_state.scroll_speed = 0

# --- LOGGAN (HEMKNAPPEN) ---
# Om bilden saknas står det "HEM" på den svarta knappen istället
logo_label = " " if logo_b64 else "HEM"
if st.button(logo_label, key="logo_home_btn"):
    st.session_state.view = "list"
    st.rerun()

st.markdown('<div class="app-top-spacer"></div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. Huvudlogik
if not os.path.exists(songs_dir):
    st.error(f"⚠️ Mappen '{songs_dir}' saknas! Skapa en mapp som heter library och lägg dina .md-filer där.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: LÅTLISTAN ---
        found_any = False
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            if valid_songs:
                found_any = True
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase; letter-spacing:1px;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for idx, song_file in enumerate(valid_songs):
                    with cols[idx % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.current_song_path = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()
        
        if not found_any:
            st.info("Inga .md-filer hittades i mappen 'library'.")

        # --- VERKTYG LÄNGST NER ---
        st.markdown('<div class="bottom-tools">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.write("**Tonart**")
            t_m, t_p = st.columns(2)
            if t_m.button("- Ton", key="t_m"): st.session_state.transpose -= 1
            if t_p.button("+ Ton", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with v_col2:
            st.write("**Auto-scroll**")
            s_m, s_p = st.columns(2)
            if s_m.button("Sakta", key="s_m"): st.session_state.scroll_speed = max(0, st.session_state.scroll_speed - 1)
            if s_p.button("Fort", key="s_p"): st.session_state.scroll_speed = min(10, st.session_state.scroll_speed + 1)
            st.write(f"Fart: {st.session_state.scroll_speed}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET (Låten) ---
        if os.path.exists(st.session_state.current_song_path):
            with open(st.session_state.current_song_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            
            song_content = transpose_chords(raw_content, st.session_state.transpose)
            scrolling_text = song_content + ("\n" * 55)

            st.markdown(f"""
                <script>
                var box = window.parent.document.getElementById("song-view-box");
                if (window.playitScroll) clearInterval(window.playitScroll);
                if ({st.session_state.scroll_speed} > 0) {{
                    var speed = (11 - {st.session_state.scroll_speed}) * 40;
                    window.playitScroll = setInterval(function() {{ if (box) box.scrollTop += 1; }}, speed);
                }}
                </script>
            """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view-box" class="song-display-area">{scrolling_text}</div>', unsafe_allow_html=True)
        else:
            st.error("Kunde inte hitta låtfilen. Gå tillbaka till arkivet.")
            if st.button("Tillbaka"):
                st.session_state.view = "list"
                st.rerun()
