import streamlit as st
import os
import re
import base64

# 1. Grundinställningar - Tvingar fram en ren layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Snyggar till filnamn för visning."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Kodar loggan så den kan bäddas in i CSS."""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    """Transponerar ackord i löpande text."""
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

# --- DESIGN (Tvingar ljust tema och rundade hörn) ---
logo_base64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* TVINGA LJUST TEMA */
    header, footer, .stApp {{ 
        background-color: #ffffff !important; 
        visibility: hidden !important;
    }}
    
    .stApp {{ 
        background-color: #ffffff !important; 
        visibility: visible !important;
    }}

    .block-container {{
        padding-top: 4rem !important; 
        background-color: #ffffff !important;
        max-width: 98% !important;
    }}

    /* LOGGAN / HEMKNAPPEN */
    .logo-anchor {{
        position: fixed;
        top: 10px;
        left: 20px;
        z-index: 10000;
        transform: rotate(-8deg);
        pointer-events: none;
    }}
    
    .logo-img-style {{
        width: 80px;
        height: auto;
        border-radius: 12px;
        border: 2px solid #000;
        background: #000;
    }}

    /* OSYNLIG KLICK-YTA FÖR LOGGAN */
    div[data-testid="stButton"]:first-child button {{
        position: fixed !important;
        top: 10px !important;
        left: 20px !important;
        width: 85px !important;
        height: 55px !important;
        z-index: 10001 !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    /* DEN STORA LÄSRUTAN */
    .song-box-style {{
        height: 88vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px;
        border: 3px solid #000000;
        border-radius: 35px; 
        font-family: 'Courier New', Courier, monospace;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 0px;
    }}

    /* KNAPPAR */
    .stButton>button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif;
    }}

    .settings-section {{
        margin-top: 40px;
        padding: 25px;
        background-color: #fcfcfc;
        border-radius: 30px;
        border: 2px dashed #000000;
    }}

    h1, h2, h3, p {{
        color: #000000 !important;
        font-family: 'Inter', sans-serif;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK & NAVIGATION ---
if "view" not in st.session_state: st.session_state.view = "list"
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# HEMKNAPP (Placeras först för att CSS-selector ska hitta den)
if st.button("HOME", key="logo_home_btn"):
    st.session_state.view = "list"
    st.rerun()

# Rita upp den visuella loggan
if logo_base64:
    st.markdown(f'<div class="logo-anchor"><img src="data:image/png;base64,{logo_base64}" class="logo-img-style"></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="logo-anchor"><div style="background:black;color:white;padding:10px;border-radius:10px;">PLAY</div></div>', unsafe_allow_html=True)

songs_dir = "library"

# --- 3. RENDERING ---
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte. Kontrollera din GitHub-struktur.")
else:
    if st.session_state.view == "list":
        # --- ARKIV-VY ---
        st.header("Arkiv")
        
        # Gå igenom mappar och hämta låtar
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Samling"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            
            if valid_songs:
                st.markdown(f"### {category.upper()}")
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.current_path = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # INSTÄLLNINGAR LÄNGST NER
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("⚙️ Verktyg & Inställningar")
        col_t, col_s = st.columns(2)
        with col_t:
            st.write("**Transponering**")
            t_min, t_plus = st.columns(2)
            if t_min.button("- Ton"): st.session_state.transpose -= 1
            if t_plus.button("+ Ton"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with col_s:
            st.write("**Auto-scroll**")
            s_min, s_plus = st.columns(2)
            if s_min.button("Saktare"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s_plus.button("Snabbare"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SCEN-VY ---
        # "Dold" tillbaka-knapp via dubbelklick
        if st.button("← TILLBAKA TILL ARKIVET", key="back_to_list"):
            st.session_state.view = "list"
            st.rerun()

        # Läs in låtfilen
        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            song_content = f.read()
        
        # Bearbeta texten
        song_content = transpose_chords(song_content, st.session_state.transpose)
        full_text = song_content + ("\n" * 50)

        # Injicera JavaScript för Dubbelklick och Scroll
        st.markdown(f"""
            <script>
            // Hitta tillbaka-knappen och dölj den
            var allBtns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            var backBtn = Array.from(allBtns).find(b => b.innerText.includes("ARKIVET"));
            if (backBtn) backBtn.style.display = 'none';

            // Dubbelklick för att visa knappen
            window.parent.document.addEventListener('dblclick', function() {{
                if (backBtn) backBtn.style.display = backBtn.style.display === 'none' ? 'block' : 'none';
            }});

            // Scroll-logik
            var container = window.parent.document.getElementById("song-box-id");
            if (window.playitScroll) clearInterval(window.playitScroll);
            if ({st.session_state.scroll} > 0) {{
                var speed = (11 - {st.session_state.scroll}) * 35;
                window.playitScroll = setInterval(function() {{
                    if (container) container.scrollTop += 1;
                }}, speed);
            }}
            </script>
        """, unsafe_allow_html=True)

        # Visa den stora rutan
        st.markdown(f'<div id="song-box-id" class="song-box-style">{full_text}</div>', unsafe_allow_html=True)
