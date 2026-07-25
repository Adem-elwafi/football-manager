import streamlit as st
from typing import Callable


def confirm_dialog(key: str, message: str, on_confirm: Callable, *args, **kwargs):
    if key not in st.session_state:
        st.session_state[key] = False
    if st.button("🗑️ Delete", key=f"{key}_btn"):
        st.session_state[key] = True
    if st.session_state[key]:
        st.warning(message)
        c1, c2 = st.columns(2)
        if c1.button("✅ Confirm", key=f"{key}_confirm"):
            on_confirm(*args, **kwargs)
            st.session_state[key] = False
            st.rerun()
        if c2.button("❌ Cancel", key=f"{key}_cancel"):
            st.session_state[key] = False
            st.rerun()
