# --- UPPDATERAD KONTROLLRAD MED STANDARD TUNING ---
st.markdown('<div class="control-row">', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6, c7 = st.columns([1,1,1,1,1,1,1]) # En extra kolumn för STD

with c1: # Transponering Ner
    if st.button("–", key="t_dn"): 
        st.session_state.transpose_val -= 1
        st.rerun()

with c2: # STANDARD TUNING SNABBVAL
    if st.button("STD", key="t_std", help="Återställ till standardstämning"):
        st.session_state.transpose_val = 0
        st.rerun()

with c3: # Transponering Upp
    if st.button("+", key="t_up"): 
        st.session_state.transpose_val += 1
        st.rerun()

with c4: # Tonart-display (Visar nuvarande offset)
    color = "green" if st.session_state.transpose_val == 0 else "red"
    st.markdown(f"<small>KEY</small><br><b style='color:{color}'>{st.session_state.transpose_val}</b>", unsafe_allow_html=True)

with c5: # Scroll ON/OFF
    scroll_icon = "⏸" if st.session_state.is_scrolling else "▶"
    if st.button(scroll_icon, key="sc_toggle"):
        st.session_state.is_scrolling = not st.session_state.is_scrolling
        st.rerun()

with c6: # Hastighet Ner
    if st.button("S-"): 
        st.session_state.scroll_speed = max(0, st.session_state.scroll_speed - 5)
        st.rerun()

with c7: # Hastighet Upp
    if st.button("S+"): 
        st.session_state.scroll_speed = min(100, st.session_state.scroll_speed + 5)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
