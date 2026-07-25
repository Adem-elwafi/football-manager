from repositories.match_repo import MatchRepository
from repositories.attendance_repo import AttendanceRepository
from repositories.payment_repo import PaymentRepository
from repositories.team_repo import TeamRepository
from repositories.player_repo import PlayerRepository
from repositories.expense_repo import ExpenseRepository
from utils.formatters import format_currency


class SummaryService:
    def __init__(
        self,
        match_repo: MatchRepository,
        attendance_repo: AttendanceRepository,
        payment_repo: PaymentRepository,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
        expense_repo: ExpenseRepository = None,
    ):
        self._match_repo = match_repo
        self._attendance_repo = attendance_repo
        self._payment_repo = payment_repo
        self._team_repo = team_repo
        self._player_repo = player_repo
        self._expense_repo = expense_repo

    def generate_summary(self, match_id: int, include_unpaid: bool = True) -> str:
        match = self._match_repo.get_by_id(match_id)
        if not match:
            return "Match not found."

        player_ids = self._attendance_repo.get_player_ids_by_match(match_id)
        attendees = []
        for pid in player_ids:
            p = self._player_repo.get_by_id(pid)
            if p:
                attendees.append(p.name)
        count = len(attendees)

        extras = self._expense_repo.total_by_match(match_id) if self._expense_repo else 0.0
        total_cost = match.stadium_cost + match.transport_cost + extras
        per_player = total_cost / count if count > 0 else 0.0

        from utils.formatters import format_date
        date_str = format_date(match.date_time)

        lines = [
            f"⚽ *Match: {date_str}*",
            "───",
            f"👥 *Attendees ({count})*",
        ]

        if attendees:
            lines.append(", ".join(attendees))

        lines.append("")
        lines.append("💰 *Costs*")
        lines.append(f"Stadium: {format_currency(match.stadium_cost)}")
        lines.append(f"Transport: {format_currency(match.transport_cost)}")
        if extras > 0:
            expense_list = self._expense_repo.get_by_match(match.id) if self._expense_repo else []
            for e in expense_list:
                lines.append(f"{e.description}: {format_currency(e.amount)}")
        lines.append("───")
        lines.append(f"Total: {format_currency(total_cost)}")
        lines.append(f"Per Player: {format_currency(per_player)}")

        if count > 0:
            total_paid = self._payment_repo.total_by_match(match_id)
            lines.append("")
            lines.append(f"💵 *Payments*")
            lines.append(f"Collected: {format_currency(total_paid)} ({sum(1 for pid in player_ids if self._payment_repo.total_by_player_and_match(match_id, pid) >= per_player)}/{count})")
            lines.append(f"Remaining: {format_currency(total_cost - total_paid)}")

            if include_unpaid:
                unpaid = []
                for pid in player_ids:
                    paid = self._payment_repo.total_by_player_and_match(match_id, pid)
                    if paid < per_player:
                        p = self._player_repo.get_by_id(pid)
                        if p:
                            unpaid.append(p.name)
                if unpaid:
                    lines.append(f"Unpaid: {', '.join(unpaid)}")

        assignments = self._team_repo.get_by_match(match_id)
        team_a, team_b = [], []
        for a in assignments:
            p = self._player_repo.get_by_id(a.player_id)
            name = p.name if p else f"Player #{a.player_id}"
            if a.team == 0:
                team_a.append(name)
            else:
                team_b.append(name)

        lines.append("")
        lines.append("🏃 *Teams*")
        lines.append(f"🔴 *Team A:* {', '.join(team_a) if team_a else 'Not set'}")
        lines.append(f"🔵 *Team B:* {', '.join(team_b) if team_b else 'Not set'}")

        if match.notes:
            lines.append("")
            lines.append(f"📝 *Notes:* {match.notes}")

        return "\n".join(lines)
