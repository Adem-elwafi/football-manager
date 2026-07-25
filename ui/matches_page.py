import streamlit as st
from typing import List
from services.match_service import MatchService
from services.attendance_service import AttendanceService
from services.payment_service import PaymentService
from services.team_service import TeamService, RandomBalancer
from services.summary_service import SummaryService
from services.player_service import PlayerService
from ui.components import status_badge, payment_badge
from utils.dates import get_next_saturday_2030
from utils.formatters import format_currency, format_date


def render(
    match_service: MatchService,
    attendance_service: AttendanceService,
    payment_service: PaymentService,
    team_service: TeamService,
    summary_service: SummaryService,
    player_service: PlayerService,
):
    st.header("🏟️ Match & Pitch")

    _render_new_match_form(match_service)
    st.divider()
    st.subheader("📋 Match History")
    _render_match_history(match_service, attendance_service, payment_service, team_service, summary_service, player_service)


def _render_new_match_form(match_service: MatchService):
    with st.container(border=True):
        st.markdown("**New Match**")
        match_dt = st.datetime_input("Schedule Match", value=get_next_saturday_2030(), label_visibility="collapsed")
        c1, c2 = st.columns(2)
        stadium_cost = c1.number_input("Stadium Cost (DT)", min_value=0.0, value=42.0, step=5.0)
        transport_cost = c2.number_input("Transport Cost (DT)", min_value=0.0, value=30.0, step=5.0)
        if st.button("📅 Create New Match", type="primary", use_container_width=True):
            match_service.create_match(match_dt, stadium_cost, transport_cost)
            st.toast("✅ Match created!", icon="✅")
            st.rerun()


def _render_match_history(
    match_service: MatchService,
    attendance_service: AttendanceService,
    payment_service: PaymentService,
    team_service: TeamService,
    summary_service: SummaryService,
    player_service: PlayerService,
):
    matches = match_service.get_all_matches()
    if not matches:
        st.info("No matches yet. Create one above.")
        return

    for match in matches:
        _render_match_card(match, match_service, attendance_service, payment_service, team_service, summary_service, player_service)


def _render_match_card(
    match,
    match_service: MatchService,
    attendance_service: AttendanceService,
    payment_service: PaymentService,
    team_service: TeamService,
    summary_service: SummaryService,
    player_service: PlayerService,
):
    expand_key = f"expand_{match.id}"
    edit_key = f"edit_{match.id}"
    delete_key = f"confirm_del_{match.id}"

    count = attendance_service.get_attendance_count(match.id)
    per_player = payment_service.calculate_per_player_cost(match.id)
    statuses = payment_service.get_payment_status(match.id)
    total_owed = sum(s.amount_owed for s in statuses.values())
    total_paid = sum(s.amount_paid for s in statuses.values())

    is_expanded = st.session_state.get(expand_key, False)
    is_editing = st.session_state.get(edit_key, False)

    with st.container(border=True):
        cols = st.columns([3, 1, 1.2, 0.5, 0.5])
        cols[0].markdown(f"**{format_date(match.date_time)}**")
        cols[1].markdown(f"👥 {count} attending")
        col2_text = f"💰 {format_currency(total_paid)} / {format_currency(total_owed)}"
        cols[2].markdown(col2_text)

        toggle_label = "▾ Hide" if is_expanded else "▸ View"
        if cols[3].button(toggle_label, key=f"toggle_{match.id}", use_container_width=True):
            st.session_state[expand_key] = not is_expanded
            st.rerun()

        if cols[4].button("🗑️", key=f"trash_{match.id}", help="Delete match"):
            st.session_state[delete_key] = True

        if st.session_state.get(delete_key, False):
            st.warning(f"Delete match on {format_date(match.date_time)}? All related data will be removed.")
            c1, c2 = st.columns(2)
            if c1.button("✅ Confirm delete", key=f"yes_del_{match.id}"):
                match_service.delete_match(match.id)
                st.session_state[delete_key] = False
                st.toast("🗑️ Match deleted.", icon="🗑️")
                st.rerun()
            if c2.button("❌ Cancel", key=f"no_del_{match.id}"):
                st.session_state[delete_key] = False
                st.rerun()

        if is_expanded:
            _render_match_detail(match, is_editing, edit_key, match_service, attendance_service, payment_service, team_service, summary_service, player_service)


def _render_match_detail(
    match, is_editing, edit_key,
    match_service, attendance_service, payment_service,
    team_service, summary_service, player_service,
):
    if is_editing:
        _render_match_edit_mode(match, edit_key, match_service, attendance_service, payment_service, team_service, summary_service, player_service)
    else:
        _render_match_view_mode(match, match_service, attendance_service, payment_service, team_service, summary_service, player_service)


def _render_match_view_mode(
    match, match_service, attendance_service,
    payment_service, team_service, summary_service, player_service,
):
    edit_key = f"edit_{match.id}"
    st.markdown(f"**Stadium:** {format_currency(match.stadium_cost)} | **Transport:** {format_currency(match.transport_cost)}")

    if match.notes:
        st.markdown(f"**Notes:** {match.notes}")

    st.markdown("**Attendees**")
    attendees = attendance_service.get_attendees(match.id)
    st.write(", ".join(p.name for p in attendees) if attendees else "None")

    _render_cost_summary(match, payment_service, attendance_service, match_service)

    st.markdown("**Teams**")
    ta = team_service.get_team_assignments(match.id)
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.markdown("**Team A**\n" + "\n".join(f"- {m['name']}" for m in ta["team_a"]))
        c2.markdown("**Team B**\n" + "\n".join(f"- {m['name']}" for m in ta["team_b"]))

    col1, col2 = st.columns([1, 1])
    if col1.button("✏️ Edit", key=f"edit_btn_{match.id}", use_container_width=True):
        st.session_state[edit_key] = True
        st.rerun()
    if col2.button("📱 Summary", key=f"summ_btn_{match.id}", use_container_width=True):
        st.session_state[f"show_summary_{match.id}"] = not st.session_state.get(f"show_summary_{match.id}", False)
        st.rerun()

    if st.session_state.get(f"show_summary_{match.id}", False):
        summary = summary_service.generate_summary(match.id)
        st.text_area("WhatsApp Summary", value=summary, height=250)


def _render_match_edit_mode(
    match, edit_key, match_service, attendance_service,
    payment_service, team_service, summary_service, player_service,
):
    st.markdown("**Edit Match**")
    date_val = st.date_input("Date", value=_parse_date(match.date_time), key=f"ed_date_{match.id}")
    time_val = st.time_input("Time", value=_parse_time(match.date_time), key=f"ed_time_{match.id}")
    c1, c2 = st.columns(2)
    new_stadium = c1.number_input("Stadium Cost", min_value=0.0, value=float(match.stadium_cost), step=5.0, key=f"ed_stad_{match.id}")
    new_transport = c2.number_input("Transport Cost", min_value=0.0, value=float(match.transport_cost), step=5.0, key=f"ed_trans_{match.id}")
    new_notes = st.text_area("Notes", value=match.notes, key=f"ed_notes_{match.id}")

    _render_attendance_editor(match.id, player_service, attendance_service)

    _render_expenses_editor(match.id, match_service, payment_service, attendance_service)

    _render_team_editor(match.id, player_service, team_service, attendance_service)

    col1, col2 = st.columns(2)
    if col1.button("💾 Save", type="primary", key=f"save_{match.id}", use_container_width=True):
        from datetime import datetime
        new_dt = datetime.combine(date_val, time_val)
        match_service.update_match(
            match.id,
            date_time=new_dt.isoformat(),
            stadium_cost=new_stadium,
            transport_cost=new_transport,
            notes=new_notes,
        )
        st.session_state[edit_key] = False
        st.toast("✅ Match updated!", icon="✅")
        st.rerun()
    if col2.button("❌ Cancel", key=f"cancel_edit_{match.id}", use_container_width=True):
        st.session_state[edit_key] = False
        st.rerun()


def _render_attendance_editor(match_id, player_service, attendance_service):
    st.markdown("**Attendance**")
    players = player_service.get_active_players()
    attendees = attendance_service.get_attendees(match_id)
    attendee_ids = {p.id for p in attendees}

    cols = st.columns(4)
    for i, p in enumerate(players):
        is_att = p.id in attendee_ids
        checked = cols[i % 4].checkbox(p.name, value=is_att, key=f"att_{match_id}_{p.id}")
        if checked != is_att:
            attendance_service.set_attendance(match_id, p.id, checked)
            st.rerun()


def _render_team_editor(match_id, player_service, team_service, attendance_service):
    st.markdown("**Teams**")
    c1, c2, c3 = st.columns(3)
    if c1.button("🔀 Random Split", key=f"gen_{match_id}", use_container_width=True):
        team_service.generate_teams(match_id)
        st.rerun()
    if c2.button("🔄 Reshuffle", key=f"reshuf_{match_id}", use_container_width=True):
        team_service.reshuffle_teams(match_id)
        st.rerun()

    ta = team_service.get_team_assignments(match_id)
    with st.container(border=True):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Team A**")
            for member in ta["team_a"]:
                is_locked = member["is_locked"]
                lock_key = f"lock_{match_id}_{member['player_id']}"
                locked = st.checkbox(f"🔒 {member['name']}", value=is_locked, key=lock_key)
                if locked != is_locked:
                    team_service.lock_player(match_id, member['player_id']) if locked else team_service.unlock_player(match_id, member['player_id'])
                    st.rerun()
        with col_b:
            st.markdown("**Team B**")
            for member in ta["team_b"]:
                is_locked = member["is_locked"]
                lock_key = f"lock_{match_id}_{member['player_id']}"
                locked = st.checkbox(f"🔒 {member['name']}", value=is_locked, key=lock_key)
                if locked != is_locked:
                    team_service.lock_player(match_id, member['player_id']) if locked else team_service.unlock_player(match_id, member['player_id'])
                    st.rerun()


def _render_cost_summary(match, payment_service, attendance_service=None, match_service=None):
    if attendance_service:
        count = attendance_service.get_attendance_count(match.id)
    else:
        count = 0
    if count == 0:
        st.info("No attendees — per-player cost cannot be calculated.")
        return
    expenses = match_service.get_expenses(match.id) if match_service else []
    total_extras = sum(e.amount for e in expenses)
    total = match.stadium_cost + match.transport_cost + total_extras
    per_player = total / count

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Cost", format_currency(total))
    m2.metric("Attendees", str(count))
    m3.metric("Per Player", format_currency(per_player))

    if expenses:
        extras_str = "; ".join(f"{e.description}: {format_currency(e.amount)}" for e in expenses)
        st.caption(f"**Extras:** {extras_str}")
    else:
        st.caption("**Extras:** None")


def _render_expenses_editor(match_id, match_service, payment_service, attendance_service=None):
    st.markdown("**Additional Expenses**")
    expenses = match_service.get_expenses(match_id)
    for exp in expenses:
        cols = st.columns([3, 1, 0.5])
        cols[0].markdown(f"{exp.description} — {format_currency(exp.amount)}")
        if cols[2].button("✕", key=f"del_exp_{exp.id}"):
            match_service.delete_expense(exp.id)
            st.rerun()

    with st.form(key=f"add_expense_{match_id}", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 0.5])
        desc = c1.text_input("Description", placeholder="e.g. Drinks", label_visibility="collapsed", key=f"exp_desc_{match_id}")
        amount = c2.number_input("Amount", min_value=0.0, step=5.0, label_visibility="collapsed", key=f"exp_amt_{match_id}")
        if c3.form_submit_button("➕", use_container_width=True):
            if desc.strip() and amount > 0:
                match_service.add_expense(match_id, desc.strip(), amount)
                st.rerun()

    if attendance_service and attendance_service.get_attendance_count(match_id) > 0:
        per_player = payment_service.calculate_per_player_cost(match_id)
        st.caption(f"Updated per-player cost: {format_currency(per_player)}")


def _parse_date(date_str: str):
    from datetime import datetime
    try:
        return datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        return get_next_saturday_2030().date()


def _parse_time(date_str: str):
    from datetime import datetime
    try:
        return datetime.fromisoformat(date_str).time()
    except (ValueError, TypeError):
        return get_next_saturday_2030().time()
