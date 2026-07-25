import streamlit as st
from services.player_service import PlayerService
from ui.components import status_badge
from utils.formatters import format_currency, format_date


def render(player_service: PlayerService):
    st.header("👥 Player Management")

    with st.form("new_player", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Player Name", placeholder="Enter full name")
        phone = c2.text_input("Phone Number", placeholder="e.g. 52 123 456")
        submitted = st.form_submit_button("➕ Add to Squad", type="primary", use_container_width=True)
        if submitted:
            if name.strip() and phone.strip():
                player_service.add_player(name.strip(), phone.strip())
                st.toast(f"✅ {name.strip()} added to squad!", icon="✅")
                st.rerun()
            else:
                st.error("Both name and phone are required.")

    st.divider()

    search_query = st.text_input("🔍 Search players", placeholder="Type name or phone...", label_visibility="collapsed")
    show_archived = st.toggle("Show archived players", value=False)

    if show_archived:
        players = player_service.search_players(search_query, include_archived=True)
    else:
        players = player_service.search_players(search_query, include_archived=False)

    if not players:
        st.info("No players found." if search_query else "No players yet. Add your first player above.")
        return

    for p in players:
        with st.container(border=True):
            cols = st.columns([2.5, 2, 1, 0.8, 0.8, 0.8])

            cols[0].markdown(f"**{p.name}**")
            cols[1].markdown(p.phone)

            with cols[2]:
                status_badge(not p.is_archived, "Active", "Archived")

            with cols[3]:
                profile_key = f"profile_{p.id}"
                if cols[3].button("📊", key=profile_key, help="View profile & stats"):
                    st.session_state[f"expanded_{p.id}"] = not st.session_state.get(f"expanded_{p.id}", False)
                    st.rerun()

            if p.is_archived:
                if cols[4].button("♻️", key=f"unarch_{p.id}", help="Restore player"):
                    player_service.unarchive_player(p.id)
                    st.toast(f"♻️ {p.name} restored.", icon="♻️")
                    st.rerun()
            else:
                if cols[4].button("📁", key=f"arch_{p.id}", help="Archive player"):
                    player_service.archive_player(p.id)
                    st.toast(f"📁 {p.name} archived.", icon="📁")
                    st.rerun()

            if cols[5].button("🗑️", key=f"del_{p.id}", help="Permanently delete"):
                st.session_state[f"confirm_del_{p.id}"] = True

            if st.session_state.get(f"confirm_del_{p.id}", False):
                st.warning(f"Permanently delete {p.name}? This cannot be undone.")
                c1, c2 = st.columns(2)
                if c1.button("✅ Yes, delete", key=f"yes_del_{p.id}"):
                    from db.connection import get_db
                    from repositories.player_repo import PlayerRepository
                    with get_db() as conn:
                        PlayerRepository(conn).delete(p.id)
                    st.session_state[f"confirm_del_{p.id}"] = False
                    st.toast(f"🗑️ {p.name} deleted.", icon="🗑️")
                    st.rerun()
                if c2.button("❌ Cancel", key=f"no_del_{p.id}"):
                    st.session_state[f"confirm_del_{p.id}"] = False
                    st.rerun()

        if st.session_state.get(f"expanded_{p.id}", False):
            _render_profile(player_service, p.id)


def _render_profile(player_service: PlayerService, player_id: int):
    stats = player_service.get_player_stats(player_id)
    with st.container(border=True):
        st.markdown("**Player Statistics**")
        m1, m2, m3 = st.columns(3)
        m1.metric("Matches Played", stats.matches_played)
        m2.metric("Attendance Rate", f"{stats.attendance_rate}%")
        m3.metric("Last Participation", format_date(stats.last_participation) if stats.last_participation else "Never")

        st.markdown("**Payments**")
        c1, c2 = st.columns(2)
        c1.metric("Total Paid", format_currency(stats.total_paid))
        c2.metric("Total Owed", format_currency(stats.total_owed))
