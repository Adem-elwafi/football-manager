from repositories.match_repo import MatchRepository
from repositories.attendance_repo import AttendanceRepository
from repositories.payment_repo import PaymentRepository
from repositories.team_repo import TeamRepository
from repositories.player_repo import PlayerRepository
from utils.formatters import format_currency


class SummaryService:
    def __init__(
        self,
        match_repo: MatchRepository,
        attendance_repo: AttendanceRepository,
        payment_repo: PaymentRepository,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
    ):
        self._match_repo = match_repo
        self._attendance_repo = attendance_repo
        self._payment_repo = payment_repo
        self._team_repo = team_repo
        self._player_repo = player_repo

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
        per_player = 0.0
        if count > 0:
            per_player = (match.stadium_cost + match.transport_cost) / count

        assignments = self._team_repo.get_by_match(match_id)
        team_a, team_b = [], []
        locked_ids = set()
        for a in assignments:
            p = self._player_repo.get_by_id(a.player_id)
            name = p.name if p else f"Player #{a.player_id}"
            if a.team == 0:
                team_a.append(name)
            else:
                team_b.append(name)
            if a.is_locked:
                locked_ids.add(a.player_id)

        lines = [f"⚽ *Match Summary: {match.date_time}*", "---"]
        lines.append(f"✅ *Confirmed Players:* {count}")
        lines.append(f"💰 *Stadium:* {format_currency(match.stadium_cost)}")
        lines.append(f"🚗 *Transport:* {format_currency(match.transport_cost)}")
        lines.append(f"💵 *Total per person:* {format_currency(per_player)}")
        lines.append("")

        if attendees:
            lines.append(f"👥 *Attendees:* {', '.join(attendees)}")

        if include_unpaid and count > 0:
            unpaid = []
            for pid in player_ids:
                paid = self._payment_repo.total_by_player_and_match(match_id, pid)
                if paid < per_player:
                    p = self._player_repo.get_by_id(pid)
                    name = p.name if p else f"Player #{pid}"
                    unpaid.append(name)
            if unpaid:
                lines.append(f"⚠️ *Unpaid:* {', '.join(unpaid)}")

        lines.append("")
        lines.append("🏃 *Teams:*")
        lines.append(f"*Team A:* {', '.join(team_a) if team_a else 'Not set'}")
        lines.append(f"*Team B:* {', '.join(team_b) if team_b else 'Not set'}")
        if locked_ids:
            lines.append("🔒 *Locked players present*")

        return "\n".join(lines)
