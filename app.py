import streamlit as st
import os
import re
import base64

# 1. Grundinställningar
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Snyggar till filnamn: EYE_OF_THE_TIGER -> Eye of the tiger"""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Konverterar bilden till ett format som CSS kan läsa direkt."""
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

# --- DESIGN (Maximerad läsyta & dolda element) ---
logo_base64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT FRÅN STREAMLIT STANDARD */
    header, footer, #MainMenu {{visibility: hidden !important;}}
    
    .block-container {{
        padding-top: 4.5rem !important; 
        max-width: 98% !important;
    }}

    /* LOGGAN (HEMKNAPPEN) */
    .logo-wrapper {{
        position: fixed;
        top: 10px;
        left: 20px;
        z-index: 9999;
        transform: rotate(-8deg);
        pointer-events: none;
    }}
    
    .logo-img-style {{
        width: 80px; /* Något mindre enligt önskemål */
        height: auto;
        border-radius: 12px;
        border: 2px solid #000;
        background: #000;
    }}

    /* OSYNLIG KNAPP OVANPÅ LOGGAN */
    div[data-testid="stButton"]:first-child button {{
        position: fixed !important;
        top: 10px !important;
        left: 20px !important;
        width: 85px !important;
        height: 55px !important;
        z-index: 10000 !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    /* MAXIMERAD LÄSRUTA */
    .song-container {{
        height: 90vh; /* Maximerad höjd */
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border: 3px solid #000000;
        border-radius: 30px; 
        font-family: 'Courier New', Courier, monospace;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    .stButton>button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State & Navigation
if "view" not in st.session_state: st.session_state.view = "list"
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- LOGGAN OCH HEMKNAPPEN ---
if st.button("HOME", key="logo_home"):
    st.session_state.view = "list"
    st.rerun()

if logo_base64:
    st.markdown(f'''
        <div class="logo-wrapper">
            <img src="data:image/png;base64,{logo_base64}" class="logo-img-style">
        </div>
    ''', unsafe_allow_html=True)

songs_dir = "library"

# 3. Logik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- ARKIVET (Sida 1) ---
        st.title("Arkiv")
        search = st.text_input("SÖK LÅT...", placeholder="Hitta låten här")

        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            filtered_files = [f for f in valid_files if search.lower() in f.lower() or search.lower() in clean_title(f).lower()]
            
            if filtered_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:15px; font-size:12px;">{category.upper()}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, filename in enumerate(filtered_files):
                    with cols[i % 2]:
                        if st.button(clean_title(filename), key=os.path.join(root, filename)):
                            st.session_state.current_path = os.path.join(root, filename)
                            st.session_state.view = "song"
                            st.rerun()

        # Verktyg längst ner
        st.write("---")
        st.subheader("⚙️ Verktyg")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Tonart**")
            tc1, tc2 = st.columns(2)
            if tc1.button("-", key="t_m"): st.session_state.transpose -= 1
            if tc2.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("**Scroll**")
            sc1, sc2 = st.columns(2)
            if sc1.button("Sakta", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if sc2.button("Fort", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")

    else:
        # --- SCENLÄGET (Sida 2) ---
        # "Tillbaka"-knappen (visas vid dubbelklick)
        if st.button("← ARKIV", key="back_btn"):
            st.session_state.view = "list"
            st.rerun()

        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = transpose_chords(content, st.session_state.transpose)
        display_text = content + ("\n" * 50)

        st.markdown(f"""
            <script>
            // Logik för dubbelklicks-menyn
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            var backBtn = Array.from(btns).find(b => b.innerText.includes("ARKIV"));
            if (backBtn) backBtn.style.display = 'none';

            window.parent.document.addEventListener('dblclick', function() {{
                if (backBtn) backBtn.style.display = backBtn.style.display === 'none' ? 'block' : 'none';
            }});

            // Auto-scroll logik
            var box = window.parent.document.getElementById("song-box");
            if (window.sInterval) clearInterval(window.sInterval);
            if ({st.session_state.scroll} > 0) {{
                var delay = (11 - {st.session_state.scroll}) * 35;
                window.sInterval = setInterval(function() {{ if (box) box.scrollTop += 1; }}, delay);
            }}
            </script>
        """, unsafe_allow_html=True)

        # Låtrutan (Nu utan rubrik och större!)
        st.markdown(f'<div id="song-box" class="song-container">{display_text}</div>', unsafe_allow_html=True)
