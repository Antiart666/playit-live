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
    """Snyggar till titlar (tar bort .md och ersätter _ med mellanslag)"""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert"""
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

# --- CSS (Pansarvagn-layout) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT STANDARD-SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* FIXA TEXTEN */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
    }}

    /* 1. DEN VISUELLA LOGGAN (Denna syns alltid) */
    .fixed-logo-img {{
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        width: 120px !important; /* Låst storlek */
        height: auto !important;
        z-index: 999998 !important;
        transform: rotate(-8deg);
        pointer-events: none; /* Gör att klick går igenom till knappen under */
    }}

    /* 2. DEN OSYNLIGA HEMKNAPPEN (Ligger exakt ovanpå bilden) */
    div[data-testid="stButton"] > button[key="home_trigger"] {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        width: 130px !important;
        height: 80px !important;
        z-index: 999999 !important;
        opacity: 0 !important; /* Gör den helt osynlig */
        background: transparent !important;
        border: none !important;
        cursor: pointer !important;
    }}

    /* 3. MELLANRUM SOM STOPPAR BOKSTAVSKAOSET */
    .app-spacer {{
        height: 125px; /* Skapar en mur som texten aldrig kan gå över */
        width: 100%;
        display: block;
    }}

    /* 4. LÄSRUTAN (MAXAD TILL 92%) */
    .stage-reader {{
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
    .tools-area {{
        margin-top: 40px;
        padding: 25px;
        background-color: #f9f9f9;
        border: 2px dashed #000;
        border-radius: 25px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK & NAVIGATION ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "speed" not in st.session_state: st.session_state.speed = 0

# RITA LOGGAN (Bilden)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="fixed-logo-img">', unsafe_allow_html=True)
else:
    st.markdown('<div class="fixed-logo-img" style="background:black;color:white;padding:10px;border-radius:10px;font-weight:900;">LOGGA</div>', unsafe_allow_html=True)

# OSYNLIG HEMKNAPP (Triggar navigering)
if st.button(" ", key="home_trigger"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas på GitHub.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.markdown('<div class="app-spacer"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, f in enumerate(valid_files):
                    with cols[i % 2]:
                        if st.button(clean_title(f), key=os.path.join(root, f)):
                            st.session_state.song_path = os.path.join(root, f)
                            st.session_state.view = "song"
                            st.rerun()

        # INSTÄLLNINGAR
        st.markdown('<div class="tools-area">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            if st.button("- Ton", key="t_m"): st.session_state.transpose -= 1
            if st.button("+ Ton", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            if st.button("Sakta", key="s_m"): st.session_state.speed = max(0, st.session_state.speed - 1)
            if st.button("Fort", key="s_p"): st.session_state.speed = min(10, st.session_state.speed + 1)
            st.write(f"Fart: {st.session_state.speed}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET ---
        # Mellanrum så rutan börjar snyggt under loggan
        st.markdown('<div style="height:75px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose)
            full_text = content + ("\n" * 55)

            # Auto-scroll (Säkrad utan window.parent)
            if st.session_state.speed > 0:
                delay = (11 - st.session_state.speed) * 45
                st.markdown(f"""
                    <script>
                    var box = document.getElementById("song-view");
                    if (window.scroller) clearInterval(window.scroller);
                    window.scroller = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {delay});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="stage-reader">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
