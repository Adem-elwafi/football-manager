from typing import Optional, List
from models.player import Player, PlayerStats
from repositories.player_repo import PlayerRepository
from repositories.attendance_repo import AttendanceRepository
from repositories.payment_repo import PaymentRepository
from repositories.match_repo import MatchRepository
from repositories.expense_repo import ExpenseRepository


class PlayerService:
    def __init__(
        self,
        repo: PlayerRepository,
        attendance_repo: AttendanceRepository = None,
        payment_repo: PaymentRepository = None,
        match_repo: MatchRepository = None,
        expense_repo: ExpenseRepository = None,
    ):
        self._repo = repo
        self._attendance_repo = attendance_repo
        self._payment_repo = payment_repo
        self._match_repo = match_repo
        self._expense_repo = expense_repo

    def add_player(self, name: str, phone: str) -> Player:
        return self._repo.add(name.strip(), phone.strip())

    def get_player(self, player_id: int) -> Optional[Player]:
        return self._repo.get_by_id(player_id)

    def search_players(self, query: str = "", include_archived: bool = False) -> List[Player]:
        if query.strip():
            return self._repo.search(query.strip(), include_archived)
        return self._repo.get_all(include_archived)

    def archive_player(self, player_id: int) -> None:
        self._repo.archive(player_id)

    def unarchive_player(self, player_id: int) -> None:
        self._repo.unarchive(player_id)

    def get_active_players(self) -> List[Player]:
        return self._repo.get_all(include_archived=False)

    def get_player_stats(self, player_id: int) -> PlayerStats:
        stats = PlayerStats(player_id=player_id)
        if not all([self._attendance_repo, self._payment_repo, self._match_repo, self._expense_repo]):
            return stats

        matches_played = self._attendance_repo.get_count_by_player(player_id)
        last_date = self._attendance_repo.get_last_match_date(player_id)

        total_matches = len(self._match_repo.get_all(limit=1000))
        rate = (matches_played / total_matches * 100) if total_matches > 0 else 0.0

        total_paid = self._payment_repo.total_by_player(player_id)

        attendee_ids = self._attendance_repo.get_match_ids_by_player(player_id)
        total_owed = 0.0
        for mid in attendee_ids:
            match = self._match_repo.get_by_id(mid)
            if not match:
                continue
            count = self._attendance_repo.get_count_by_match(mid)
            if count == 0:
                continue
            extras = self._expense_repo.total_by_match(mid)
            total_owed += (match.stadium_cost + match.transport_cost + extras) / count

        return PlayerStats(
            player_id=player_id,
            matches_played=matches_played,
            attendance_rate=round(rate, 1),
            last_participation=last_date,
            total_paid=round(total_paid, 2),
            total_owed=round(total_owed, 2),
        )
