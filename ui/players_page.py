import streamlit as st
from services.player_service import PlayerService


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
    st.subheader("Current Squad")

    players = player_service.get_active_players()
    if not players:
        st.info("No players yet. Add your first player above.")
        return

    for p in players:
        with st.container(border=True):
            cols = st.columns([3, 3, 1])
            cols[0].markdown(f"**{p.name}**")
            cols[1].markdown(p.phone)
            if cols[2].button("🗑️", key=f"del_{p.id}", help="Delete player (irreversible)"):
                st.error(f"Are you sure you want to permanently delete {p.name}?")
                c1, c2 = st.columns(2)
                if c1.button("✅ Yes, delete", key=f"confirm_del_{p.id}"):
                    from db.connection import get_db
                    from repositories.player_repo import PlayerRepository
                    with get_db() as conn:
                        PlayerRepository(conn).delete(p.id)
                    st.toast(f"🗑️ {p.name} deleted.", icon="🗑️")
                    st.rerun()
                if c2.button("❌ Cancel", key=f"cancel_del_{p.id}"):
                    st.rerun()
