from dataclasses import dataclass
from typing import Dict
from repositories.payment_repo import PaymentRepository
from repositories.match_repo import MatchRepository
from repositories.attendance_repo import AttendanceRepository
from repositories.expense_repo import ExpenseRepository
from repositories.player_repo import PlayerRepository


@dataclass
class PaymentStatus:
    player_id: int
    player_name: str
    amount_owed: float
    amount_paid: float
    is_full: bool


class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        match_repo: MatchRepository,
        attendance_repo: AttendanceRepository,
        expense_repo: ExpenseRepository,
        player_repo: PlayerRepository,
    ):
        self._payment_repo = payment_repo
        self._match_repo = match_repo
        self._attendance_repo = attendance_repo
        self._expense_repo = expense_repo
        self._player_repo = player_repo

    def calculate_per_player_cost(self, match_id: int) -> float:
        match = self._match_repo.get_by_id(match_id)
        if not match:
            return 0.0
        count = self._attendance_repo.get_count_by_match(match_id)
        if count == 0:
            return 0.0
        extras = self._expense_repo.total_by_match(match_id)
        total = match.stadium_cost + match.transport_cost + extras
        return total / count

    def get_payment_status(self, match_id: int) -> Dict[int, PaymentStatus]:
        match = self._match_repo.get_by_id(match_id)
        if not match:
            return {}
        count = self._attendance_repo.get_count_by_match(match_id)
        extras = self._expense_repo.total_by_match(match_id)
        per_player = 0.0
        if count > 0:
            per_player = (match.stadium_cost + match.transport_cost + extras) / count

        player_ids = self._attendance_repo.get_player_ids_by_match(match_id)
        statuses = {}
        for pid in player_ids:
            player = self._player_repo.get_by_id(pid)
            paid = self._payment_repo.total_by_player_and_match(match_id, pid)
            statuses[pid] = PaymentStatus(
                player_id=pid,
                player_name=player.name if player else f"Player #{pid}",
                amount_owed=per_player,
                amount_paid=paid,
                is_full=paid >= per_player,
            )
        return statuses

    def record_payment(self, match_id: int, player_id: int, amount: float) -> None:
        self._payment_repo.add(match_id, player_id, amount)

    def undo_payment(self, match_id: int, player_id: int) -> None:
        self._payment_repo.delete_by_player_and_match(match_id, player_id)

    def mark_all_paid(self, match_id: int) -> None:
        per_player = self.calculate_per_player_cost(match_id)
        if per_player <= 0:
            return
        player_ids = self._attendance_repo.get_player_ids_by_match(match_id)
        for pid in player_ids:
            paid = self._payment_repo.total_by_player_and_match(match_id, pid)
            if paid < per_player:
                self._payment_repo.add(match_id, pid, per_player - paid)
