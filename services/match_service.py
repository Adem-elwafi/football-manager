from typing import Optional, List
from datetime import datetime
from models.match import Match
from models.expense import Expense
from repositories.match_repo import MatchRepository
from repositories.expense_repo import ExpenseRepository


class MatchService:
    def __init__(self, repo: MatchRepository, expense_repo: ExpenseRepository = None):
        self._repo = repo
        self._expense_repo = expense_repo

    def create_match(self, date_time: datetime, stadium_cost: float, transport_cost: float) -> Match:
        return self._repo.add(
            date_time.isoformat(),
            stadium_cost,
            transport_cost,
        )

    def get_match(self, match_id: int) -> Optional[Match]:
        return self._repo.get_by_id(match_id)

    def get_all_matches(self, limit: int = 50) -> List[Match]:
        return self._repo.get_all(limit)

    def update_match(self, match_id: int, **fields) -> Optional[Match]:
        return self._repo.update(match_id, **fields)

    def delete_match(self, match_id: int) -> None:
        self._repo.delete(match_id)

    def get_expenses(self, match_id: int) -> List[Expense]:
        if not self._expense_repo:
            return []
        return self._expense_repo.get_by_match(match_id)

    def add_expense(self, match_id: int, description: str, amount: float) -> Optional[Expense]:
        if not self._expense_repo:
            return None
        return self._expense_repo.add(match_id, description.strip(), amount)

    def delete_expense(self, expense_id: int) -> None:
        if self._expense_repo:
            self._expense_repo.delete(expense_id)
