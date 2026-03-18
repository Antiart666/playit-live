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

# --- DESIGN (Modern, Rundad & Logga som knapp) ---
logo_base64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
    }}

    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 98% !important;
    }}

    /* Logga-knapp styling */
    .logo-btn-container {{
        position: absolute;
        top: 0px;
        left: 20px;
        z-index: 10001;
        transform: rotate(-8deg);
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .logo-btn-container:hover {{ transform: rotate(-4deg) scale(1.05); }}
    
    .logo-img {{
        width: 120px; /* Justera storleken på loggan här */
        height: auto;
        border-radius: 15px;
        border: 2px solid #000;
        background: #000; /* Bakgrund ifall bilden är transparent */
    }}

    /* Låtrutan (Stage Mode) */
    .song-container {{
        height: 92vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border: 3px solid #000000;
        border-radius: 30px; 
        font-family: 'Courier New', Courier, monospace;
        font-size: 18px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* Knappar */
    .stButton>button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }}
    
    /* Göm Streamlits standard-knapp för loggan men behåll funktionen */
    .invisible-logo-button {{
        position: absolute;
        top: 0;
        left: 20px;
        width: 120px;
        height: 60px;
        opacity: 0;
        z-index: 10002;
    }}

    .settings-area {{
        margin-top: 50px;
        padding: 30px;
        background-color: #f9f9f9;
        border-radius: 30px;
        border: 2px dashed #ccc;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State Management
if "view" not in st.session_state: st.session_state.view = "list"
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- LOGGA-KNAPPEN (HEM-FUNKTION) ---
# Vi lägger en osynlig Streamlit-knapp ovanpå den snygga loggan
if st.button("HOME", key="logo_home_click"):
    st.session_state.view = "list"
    st.rerun()

# Rita upp den snygga loggan (visuellt)
if logo_base64:
    st.markdown(f'''
        <div class="logo-btn-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-img">
        </div>
    ''', unsafe_allow_html=True)
else:
    # Placeholder om bilden saknas
    st.markdown('<div class="logo-btn-container"><div style="color:white; background:black; padding:10px; border-radius:10px;">PLAYIT</div></div>', unsafe_allow_html=True)

# Gör knappen osynlig men klickbar exakt där loggan är
st.markdown('<div class="invisible-logo-button"></div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. App-logik
if not os.path.exists(songs_dir):
    st.error("Ladda upp 'library'-mappen och 'logo.png' på GitHub!")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.title("Arkiv")
        search = st.text_input("Sök låt...", "")

        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            filtered_files = [f for f in valid_files if search.lower() in f.lower() or search.lower() in clean_title(f).lower()]
            
            if filtered_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:12px;">{category.upper()}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, filename in enumerate(filtered_files):
                    with cols[i % 2]:
                        if st.button(clean_title(filename), key=os.path.join(root, filename)):
                            st.session_state.current_path = os.path.join(root, filename)
                            st.session_state.view = "song"
                            st.rerun()

        # --- INSTÄLLNINGAR LÄNGST NER ---
        st.markdown('<div class="settings-area">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        set_col1, set_col2 = st.columns(2)
        with set_col1:
            st.write("**Tonart**")
            t1, t2 = st.columns(2)
            if t1.button("-"): st.session_state.transpose -= 1
            if t2.button("+"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with set_col2:
            st.write("**Scroll**")
            s1, s2 = st.columns(2)
            if s1.button("Sakta"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s2.button("Fort"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET ---
        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = transpose_chords(content, st.session_state.transpose)
        display_text = content + ("\n" * 45)

        # JavaScript för Dubbelklick & Scroll
        st.markdown(f"""
            <script>
            // Logik för att visa "Tillbaka"-knappen vid dubbelklick
            var buttons = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            var backBtn = buttons[0]; // Första knappen i Streamlit-ordningen
            if (backBtn) backBtn.style.display = 'none';

            window.parent.document.addEventListener('dblclick', function() {{
                if (backBtn) backBtn.style.display = backBtn.style.display === 'none' ? 'block' : 'none';
            }});

            // Scroll
            var box = window.parent.document.getElementById("song-box");
            if (window.sInterval) clearInterval(window.sInterval);
            if ({st.session_state.scroll} > 0) {{
                var delay = (11 - {st.session_state.scroll}) * 35;
                window.sInterval = setInterval(function() {{ if (box) box.scrollTop += 1; }}, delay);
            }}
            </script>
        """, unsafe_allow_html=True)

        # Hem-knappen som bara syns vid dubbelklick
        if st.button("← ARKIV", key="manual_back"):
            st.session_state.view = "list"
            st.rerun()

        st.markdown(f'<div id="song-box" class="song-container">{display_text}</div>', unsafe_allow_html=True)
