import streamlit as st


def status_badge(is_active: bool, label_active: str = "Active", label_inactive: str = "Inactive"):
    if is_active:
        st.markdown(f"<span style='background-color:#10b981;color:white;padding:2px 10px;border-radius:12px;font-size:0.8em'>{label_active}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='background-color:#6b7280;color:white;padding:2px 10px;border-radius:12px;font-size:0.8em'>{label_inactive}</span>", unsafe_allow_html=True)


def payment_badge(amount_paid: float, amount_owed: float):
    if amount_owed <= 0:
        return
    ratio = amount_paid / amount_owed if amount_owed > 0 else 0
    if ratio >= 1:
        st.markdown(f"<span style='background-color:#10b981;color:white;padding:2px 10px;border-radius:12px;font-size:0.8em'>Paid</span>", unsafe_allow_html=True)
    elif ratio > 0:
        st.markdown(f"<span style='background-color:#f59e0b;color:white;padding:2px 10px;border-radius:12px;font-size:0.8em'>Partial</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='background-color:#ef4444;color:white;padding:2px 10px;border-radius:12px;font-size:0.8em'>Unpaid</span>", unsafe_allow_html=True)
