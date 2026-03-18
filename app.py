import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Tvingar fram ljus layout
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
    """Kodar bilden så den kan bäddas in i CSS."""
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

# --- DESIGN (Inter-font, Rundade hörn och Ren Logga) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* TVINGA VITT TEMA OCH DÖLJ ALLT SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GÖR ALL TEXT SVART */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif; }}

    .block-container {{
        padding-top: 2rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* LOGGAN (Ingen svart ram nu!) */
    .logo-anchor {{
        position: fixed;
        top: 15px;
        left: 20px;
        z-index: 9999;
        transform: rotate(-8deg);
        pointer-events: none; /* Låter klicket gå igenom till knappen under */
    }}
    
    .logo-img-style {{
        width: 110px;
        height: auto;
        /* Borttaget: border och background för att slippa svarta ramen */
    }}

    /* DEN OSYNLIGA HEM-KNAPPEN (Som ligger exakt över loggan) */
    div[data-testid="stButton"]:first-child button {{
        position: fixed !important;
        top: 10px !important;
        left: 15px !important;
        width: 120px !important;
        height: 80px !important;
        z-index: 10000 !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }}

    /* MELLANRUM SÅ ATT TEXTEN INTE BUNTAR IHOP SIG */
    .spacer-box {{
        height: 110px;
        width: 100%;
    }}

    /* LÄSRUTAN (MAXAD) */
    .song-container-style {{
        height: 86vh; 
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
    }}

    /* ARKIV-KNAPPAR */
    .stButton>button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
    }}

    .settings-box {{
        margin-top: 40px;
        padding: 25px;
        background-color: #fcfcfc;
        border-radius: 30px;
        border: 2px dashed #000000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State & Navigation
if "view" not in st.session_state: st.session_state.view = "list"
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- MAGISK HEMKNAPP (Osynlig men klickbar) ---
# Denna ligger först så CSS-väljaren (:first-child) hittar den
if st.button("HOME_LINK", key="logo_home_redirect"):
    st.session_state.view = "list"
    st.rerun()

# Visuell logga (Utan ram)
if logo_b64:
    st.markdown(f'<div class="logo-anchor"><img src="data:image/png;base64,{logo_b64}" class="logo-img-style"></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="logo-anchor"><div style="background:black;color:white;padding:10px;border-radius:10px;font-weight:900;">PLAYIT</div></div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. App-logik
# Spacer som förhindrar att Arkivet hamnar "bakom" loggan
st.markdown('<div class="spacer-box"></div>', unsafe_allow_html=True)

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas på GitHub.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.header("Arkiv")
        
        # Hämta låtar (Ingen sökfunktion)
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            
            if valid_songs:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:12px; letter-spacing:1px;">{category.upper()}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.current_path = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # --- INSTÄLLNINGAR LÄNGST NER ---
        st.markdown('<div class="settings-box">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Tonart**")
            t_min, t_plus = st.columns(2)
            if t_min.button("-", key="t_m"): st.session_state.transpose -= 1
            if t_plus.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("**Scroll**")
            s_min, s_plus = st.columns(2)
            if s_min.button("Sakta", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s_plus.button("Fort", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET (Låten) ---
        # Back-knapp som endast syns vid dubbelklick
        if st.button("← ARKIV", key="manual_back_link"):
            st.session_state.view = "list"
            st.rerun()

        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        # Bearbeta text
        display_text = transpose_chords(raw_text, st.session_state.transpose)
        display_text += ("\n" * 45) # Extra luft i botten

        # JavaScript för Dubbelklick & Scroll (Säkrad för mobiler)
        st.markdown(f"""
            <script>
            // Hitta tillbaka-knappen och dölj den
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            var backBtn = Array.from(btns).find(b => b.innerText.includes("ARKIV"));
            if (backBtn) backBtn.style.display = 'none';

            // Visa vid dubbelklick
            window.parent.document.addEventListener('dblclick', function() {{
                if (backBtn) backBtn.style.display = (backBtn.style.display === 'none') ? 'block' : 'none';
            }});

            // Scroll-logik
            var container = window.parent.document.getElementById("song-rutan-id");
            if (window.playitScroll) clearInterval(window.playitScroll);
            if ({st.session_state.scroll} > 0) {{
                var speed = (11 - {st.session_state.scroll}) * 40;
                window.playitScroll = setInterval(function() {{
                    if (container) container.scrollTop += 1;
                }}, speed);
            }}
            </script>
        """, unsafe_allow_html=True)

        # Rendera rutan
        st.markdown(f'<div id="song-rutan-id" class="song-container-style">{display_text}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
