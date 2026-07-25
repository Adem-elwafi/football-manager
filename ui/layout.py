import streamlit as st
from db.connection import get_db
from db.schema import init_db

from repositories.player_repo import PlayerRepository
from repositories.match_repo import MatchRepository
from repositories.attendance_repo import AttendanceRepository
from repositories.payment_repo import PaymentRepository
from repositories.expense_repo import ExpenseRepository
from repositories.team_repo import TeamRepository

from services.player_service import PlayerService
from services.match_service import MatchService
from services.attendance_service import AttendanceService
from services.payment_service import PaymentService
from services.team_service import TeamService
from services.summary_service import SummaryService


def main():
    st.set_page_config(page_title="Football Match Manager", layout="wide", page_icon="⚽")
    st.title("⚽ Football Match Manager")

    init_db()

    with get_db() as conn:
        player_repo = PlayerRepository(conn)
        match_repo = MatchRepository(conn)
        attendance_repo = AttendanceRepository(conn)
        payment_repo = PaymentRepository(conn)
        expense_repo = ExpenseRepository(conn)
        team_repo = TeamRepository(conn)

        player_service = PlayerService(player_repo, attendance_repo, payment_repo, match_repo, expense_repo)
        match_service = MatchService(match_repo, expense_repo)
        attendance_service = AttendanceService(attendance_repo, player_repo)
        payment_service = PaymentService(
            payment_repo, match_repo, attendance_repo, expense_repo, player_repo
        )
        team_service = TeamService(team_repo, attendance_repo, player_repo)
        summary_service = SummaryService(
            match_repo, attendance_repo, payment_repo, team_repo, player_repo
        )

        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Go to",
            ["Players", "Matches"],
            label_visibility="collapsed",
        )

        if page == "Players":
            from ui.players_page import render as render_players
            render_players(player_service)
        elif page == "Matches":
            from ui.matches_page import render as render_matches
            render_matches(
                match_service,
                attendance_service,
                payment_service,
                team_service,
                summary_service,
                player_service,
            )
