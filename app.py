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
    """Gör EYE_OF_THE_TIGER till Eye of the tiger"""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
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

    /* TVINGA VITT TEMA OCH DÖLJ ALLT FRÅN STREAMLIT */
    header, footer, #MainMenu {{ visibility: hidden !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GÖR ALL TEXT SVART */
    h1, h2, h3, p, span, div, label, li, button {{ 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important; 
    }}

    .block-container {{
        padding-top: 1rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* DEN SNEDSTÄLLDA LOGGAN */
    .logo-box {{
        position: fixed;
        top: 15px;
        left: 20px;
        z-index: 99999;
        transform: rotate(-8deg);
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .logo-box:hover {{ transform: rotate(-4deg) scale(1.05); }}
    
    .logo-img {{
        width: 140px; /* Större och tydligare */
        height: auto;
    }}

    /* SKYDDSZON - FÖRHINDRAR ATT TEXT HAMNAR BAKOM LOGGAN */
    .app-header-spacer {{
        height: 130px;
        width: 100%;
        display: block;
    }}

    /* LÄSRUTAN (MAXAD) */
    .song-wrapper {{
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

    /* VERKTYGSBOX LÄNGST NER */
    .settings-tray {{
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
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- LOGGAN SOM HEMKNAPP (STABIL VERSION) ---
# Vi använder en osynlig Streamlit-knapp som är 100% driftsäker
if st.sidebar.button("RESET APP", key="sidebar_reset"):
    st.session_state.view = "list"
    st.rerun()

# Logga och klick-skript
if logo_b64:
    st.markdown(f"""
        <div class="logo-box" id="logo-home-trigger">
            <img src="data:image/png;base64,{logo_b64}" class="logo-img">
        </div>
        <script>
        // Ett litet skript som klickar på Streamlits reset-knapp när man trycker på loggan
        var logo = window.parent.document.getElementById("logo-home-trigger");
        if (logo) {{
            logo.onclick = function() {{
                var btns = window.parent.document.querySelectorAll('button');
                var resetBtn = Array.from(btns).find(b => b.innerText.includes("RESET APP"));
                if (resetBtn) resetBtn.click();
            }};
        }}
        </script>
    """, unsafe_allow_html=True)
else:
    # Om logo.png saknas på GitHub
    st.error("Filen 'logo.png' saknas på GitHub! Ladda upp den i huvudmappen.")

# Spacer för att trycka ner innehållet under loggan
st.markdown('<div class="app-header-spacer"></div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. App-logik
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
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:12px;">{category.upper()}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.current_path = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # --- INSTÄLLNINGAR LÄNGST NER ---
        st.markdown('<div class="settings-tray">', unsafe_allow_html=True)
        st.subheader("⚙️ Verktyg")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Tonart**")
            t_m, t_p = st.columns(2)
            if t_m.button("- Ton", key="t_m"): st.session_state.transpose -= 1
            if t_p.button("+ Ton", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("**Scroll**")
            s_m, s_p = st.columns(2)
            if s_m.button("Saktare", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s_p.button("Snabbare", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET (Låten) ---
        # Back-knapp som syns vid dubbelklick
        if st.button("← ARKIV", key="manual_back_link"):
            st.session_state.view = "list"
            st.rerun()

        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        content = transpose_chords(raw_text, st.session_state.transpose)
        display_text = content + ("\n" * 50)

        # JavaScript för Dubbelklick & Scroll
        st.markdown(f"""
            <script>
            // Hitta tillbaka-knappen och dölj den
            var btns = window.parent.document.querySelectorAll('button');
            var backBtn = Array.from(btns).find(b => b.innerText.includes("ARKIV"));
            if (backBtn) {{
                var container = backBtn.parentElement.parentElement.parentElement;
                container.style.display = 'none';
                
                window.parent.document.addEventListener('dblclick', function() {{
                    container.style.display = (container.style.display === 'none') ? 'block' : 'none';
                }});
            }}

            // Scroll-logik
            var box = window.parent.document.getElementById("song-container-id");
            if (window.playitScroll) clearInterval(window.playitScroll);
            if ({st.session_state.scroll} > 0) {{
                var speed = (11 - {st.session_state.scroll}) * 40;
                window.playitScroll = setInterval(function() {{ if (box) box.scrollTop += 1; }}, speed);
            }}
            </script>
        """, unsafe_allow_html=True)

        st.markdown(f'<div id="song-container-id" class="song-wrapper">{display_text}</div>', unsafe_allow_html=True)
