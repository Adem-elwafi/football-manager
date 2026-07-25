import streamlit as st
from services.match_service import MatchService
from services.payment_service import PaymentService
from services.attendance_service import AttendanceService
from ui.components import payment_badge
from utils.formatters import format_currency, format_date


def render(
    match_service: MatchService,
    payment_service: PaymentService,
    attendance_service: AttendanceService,
):
    st.header("💵 Payment Dashboard")

    matches = match_service.get_all_matches()
    if not matches:
        st.info("No matches yet. Create a match first.")
        return

    match_options = {format_date(m.date_time): m.id for m in matches}
    selected_label = st.selectbox("Select Match", list(match_options.keys()))
    match_id = match_options[selected_label]

    match = match_service.get_match(match_id)
    if not match:
        return

    statuses = payment_service.get_payment_status(match_id)
    count = attendance_service.get_attendance_count(match_id)

    total_owed = sum(s.amount_owed for s in statuses.values())
    total_paid = sum(s.amount_paid for s in statuses.values())
    num_unpaid = sum(1 for s in statuses.values() if not s.is_full)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Collected", format_currency(total_paid))
    m2.metric("Total Owed", format_currency(total_owed))
    m3.metric("Remaining", format_currency(total_owed - total_paid))
    m4.metric("Unpaid Players", str(num_unpaid))

    st.divider()

    if num_unpaid > 0:
        if st.button("✅ Mark All Paid", type="primary", use_container_width=True):
            st.session_state[f"confirm_mark_all_{match_id}"] = True

        if st.session_state.get(f"confirm_mark_all_{match_id}", False):
            st.warning("Mark all attending players as fully paid?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, mark all paid", key=f"yes_all_{match_id}"):
                payment_service.mark_all_paid(match_id)
                st.session_state[f"confirm_mark_all_{match_id}"] = False
                st.toast("✅ All players marked as paid!", icon="✅")
                st.rerun()
            if c2.button("Cancel", key=f"no_all_{match_id}"):
                st.session_state[f"confirm_mark_all_{match_id}"] = False
                st.rerun()

    st.subheader("Player Payments")
    cols = st.columns([2, 1, 1, 1, 1])
    cols[0].markdown("**Player**")
    cols[1].markdown("**Owed**")
    cols[2].markdown("**Paid**")
    cols[3].markdown("**Status**")
    cols[4].markdown("**Action**")

    for pid, s in statuses.items():
        cols = st.columns([2, 1, 1, 1, 1])
        cols[0].markdown(s.player_name)
        cols[1].markdown(format_currency(s.amount_owed))
        cols[2].markdown(format_currency(s.amount_paid))
        with cols[3]:
            payment_badge(s.amount_paid, s.amount_owed)

        if s.is_full:
            if cols[4].button("↩️ Undo", key=f"undo_{match_id}_{pid}", help="Mark as unpaid"):
                payment_service.undo_payment(match_id, pid)
                st.toast(f"↩️ {s.player_name} marked unpaid.", icon="↩️")
                st.rerun()
        else:
            if cols[4].button("✅ Pay", key=f"pay_{match_id}_{pid}", help="Mark as paid"):
                payment_service.record_payment(match_id, pid, s.amount_owed)
                st.toast(f"✅ {s.player_name} marked paid.", icon="✅")
                st.rerun()

    per_player = payment_service.calculate_per_player_cost(match_id)
    if count > 0:
        st.caption(f"Per-player cost for this match: {format_currency(per_player)} ({count} attendees)")
