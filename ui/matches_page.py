import streamlit as st
from typing import List
from models.match import Match
from services.match_service import MatchService
from services.attendance_service import AttendanceService
from services.payment_service import PaymentService
from services.team_service import TeamService
from services.summary_service import SummaryService
from utils.dates import get_next_saturday_2030
from utils.formatters import format_currency, format_date


def render(
    match_service: MatchService,
    attendance_service: AttendanceService,
    payment_service: PaymentService,
    team_service: TeamService,
    summary_service: SummaryService,
):
    st.header("🏟️ Match & Pitch")

    with st.expander("⚙️ New Match Configuration", expanded=True):
        match_dt = st.datetime_input("Schedule Match", value=get_next_saturday_2030())
        c1, c2 = st.columns(2)
        stadium_cost = c1.number_input("Stadium Cost (DT)", min_value=0.0, value=42.0, step=5.0)
        transport_cost = c2.number_input("Transport Cost (DT)", min_value=0.0, value=30.0, step=5.0)
        if st.button("📅 Create New Match", type="primary", use_container_width=True):
            match_service.create_match(match_dt, stadium_cost, transport_cost)
            st.toast("✅ Match created!", icon="✅")
            st.rerun()

    st.divider()
    st.subheader("📋 Match History")

    matches = match_service.get_all_matches()
    if not matches:
        st.info("No matches yet. Create one above.")
        return

    for match in matches:
        with st.container(border=True):
            cols = st.columns([3, 1, 1])
            cols[0].markdown(f"**{format_date(match.date_time)}**")
            count = attendance_service.get_attendance_count(match.id)
            cols[1].markdown(f"👥 {count} attending")
            cols[2].markdown(f"💰 {format_currency(match.stadium_cost + match.transport_cost)}")

            if st.button("📂 Open", key=f"open_{match.id}", use_container_width=True):
                st.session_state["active_match_id"] = match.id
                st.rerun()
