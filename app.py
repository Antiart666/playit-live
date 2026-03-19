import streamlit as st
import re
import time
from pathlib import Path

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(
    page_title="PlayIt! Stage Mode",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "transpose_val" not in st.session_state:
    st.session_state.transpose_val = 0
if "scroll_speed" not in st.session_state:
    st.session_state.scroll_speed = 0
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "is_scrolling" not in st.session_state:
    st.session_state.is_scrolling = False

# --- 2. TRANSPONERINGSLOGIK ---
def transpose_chord(chord, steps):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Regex för att dela upp ackordet (t.ex. [F#m7] -> F#, m7)
    pattern = r"([A-G]#?)(.*)"
    match = re.match(pattern, chord)
    if not match:
        return chord
    
    root, suffix = match.groups()
    if root not in notes:
        return chord
    
    current_index = notes.index(root)
    new_index = (current_index + steps) % 12
    return f"{notes[new_index]}{suffix}"

def process_lyrics(text, steps):
    if steps == 0:
        return text
    # Hitta allt inom klamrar [C], [Am7] etc.
    return re.sub(r"\[(.*?)\]", lambda m: f"[{transpose_chord(m.group(1), steps)}]", text)

# --- 3. UI & CSS (MATERIAL DESIGN 3 / MOBILE FIRST) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

    /* Clean Stage Mode */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #1C1B1F !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* Låttext-område */
    .lyrics-container {{
        font-family: 'Roboto Mono', monospace !important;
        font-size: {st.session_state.font_size}px !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
        padding: 20px 20px 180px 20px;
        color: #1C1B1F;
    }}
    
    .chord {{
        color: #6750A4;
        font-weight: 700;
    }}

    /* STICKY CONTROL PANEL (BOTTOM) */
    .sticky-controls {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #F3F0F7;
        border-top: 1px solid #CAC4D0;
        padding: 15px;
        z-index: 9999;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
    }}

    /* Touch-vänliga knappar (min 44px) */
    .stButton > button {{
        min-height: 48px !important;
        min-width: 48px !important;
        border-radius: 12px !important;
        background-color: #EADDFF !important;
        color: #21005D !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    
    .active-scroll {{
        background-color: #6750A4 !important;
        color: white !important;
    }}

    /* Göm input-fält (Masterprompt 1.0 skydd) */
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION (MASTERPROMPT 1.0 REFINED) ---
# Header för logga och snabbval
t_col1, t_col2 = st.columns([2, 1])
with t_col1:
    st.title("🎸 PlayIt!")
with t_col2:
    if st.button("RESET", use_container_width=True):
        st.session_state.transpose_val = 0
        st.session_state.scroll_speed = 0
        st.session_state.is_scrolling = False
        st.rerun()

# --- 5. LÅT-INNEHÅLL ---
# Exempel-låt om library är tomt
sample_lyrics = """[G] Amazing Grace, how [C] sweet the [G] sound
That [G] saved a wretch like [D7] me
I [G] once was lost, but [C] now am [G] found
Was [G] blind but [D] now I [G] see"""

# Här skulle get_songs() från Masterprompt 1.0 ligga
processed_text = process_lyrics(sample_lyrics, st.session_state.transpose_val)

# Rendera ackorden med färg (Regex för display)
display_text = re.sub(r"\[(.*?)\]", r'<span class="chord">[\1]</span>', processed_text)
st.markdown(f'<div class="lyrics-container">{display_text}</div>', unsafe_allow_html=True)

# --- 6. STICKY CONTROL PANEL ---
with st.container():
    st.markdown('<div class="sticky-controls">', unsafe_allow_html=True)
    
    # Rad 1: Transponering & Textstorlek
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        if st.button("–", key="t_down"): 
            st.session_state.transpose_val -= 1
            st.rerun()
    with c2:
        st.markdown(f"<center>Tone<br><b>{st.session_state.transpose_val}</b></center>", unsafe_allow_html=True)
    with c3:
        if st.button("+", key="t_up"): 
            st.session_state.transpose_val += 1
            st.rerun()
    with c4:
        if st.button("A+", key="f_up"):
            st.session_state.font_size += 2
            st.rerun()

    # Rad 2: Scroll
    s_col1, s_col2 = st.columns([3, 1])
    with s_col1:
        st.session_state.scroll_speed = st.slider("Scroll Speed", 0, 100, st.session_state.scroll_speed)
    with s_col2:
        scroll_label = "STOP" if st.session_state.is_scrolling else "PLAY"
        if st.button(scroll_label, key="scroll_btn", type="primary"):
            st.session_state.is_scrolling = not st.session_state.is_scrolling
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. JAVASCRIPT ENGINE (SMOOTH SCROLL) ---
if st.session_state.is_scrolling and st.session_state.scroll_speed > 0:
    # Beräkna intervall baserat på slider (0-100)
    delay = (101 - st.session_state.scroll_speed) / 2
    st.components.v1.html(f"""
        <script>
        var scrollInterval = setInterval(function() {{
            window.parent.window.scrollBy(0, 1);
        }}, {delay});
        </script>
    """, height=0)

# Scroll-to-top vid reset
if st.session_state.transpose_val == 0 and not st.session_state.is_scrolling:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
