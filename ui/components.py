import streamlit as st
from datetime import datetime


def _badge_html(text: str, bg_color: str, text_color: str = "white"):
    return f"<span style='background-color:{bg_color};color:{text_color};padding:2px 10px;border-radius:12px;font-size:0.8em;white-space:nowrap'>{text}</span>"


def status_badge(is_active: bool, label_active: str = "Active", label_inactive: str = "Inactive"):
    if is_active:
        st.markdown(_badge_html(label_active, "#10b981"), unsafe_allow_html=True)
    else:
        st.markdown(_badge_html(label_inactive, "#6b7280"), unsafe_allow_html=True)


def payment_badge(amount_paid: float, amount_owed: float):
    if amount_owed <= 0:
        return
    ratio = amount_paid / amount_owed if amount_owed > 0 else 0
    if ratio >= 1:
        st.markdown(_badge_html("Paid", "#10b981"), unsafe_allow_html=True)
    elif ratio > 0:
        st.markdown(_badge_html("Partial", "#f59e0b"), unsafe_allow_html=True)
    else:
        st.markdown(_badge_html("Unpaid", "#ef4444"), unsafe_allow_html=True)


def match_status_badge(date_time_str: str, match_id: int = None, is_current: bool = False):
    try:
        dt = datetime.fromisoformat(date_time_str)
        now = datetime.now()
        if is_current:
            st.markdown(_badge_html("Current", "#3b82f6"), unsafe_allow_html=True)
        elif dt > now:
            st.markdown(_badge_html("Upcoming", "#8b5cf6"), unsafe_allow_html=True)
        else:
            st.markdown(_badge_html("Past", "#6b7280"), unsafe_allow_html=True)
    except (ValueError, TypeError):
        pass


def confirm_popover(trigger_label: str, key: str, message: str, on_confirm, icon: str = "⚠️", **kwargs):
    with st.popover(icon, use_container_width=True):
        st.warning(message)
        c1, c2 = st.columns(2)
        if c1.button("✅ Confirm", key=f"{key}_yes", use_container_width=True):
            on_confirm(**kwargs)
            st.rerun()
        if c2.button("❌ Cancel", key=f"{key}_no", use_container_width=True):
            st.rerun()
