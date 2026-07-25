from typing import Optional, List
from datetime import datetime
from models.match import Match
from repositories.match_repo import MatchRepository


class MatchService:
    def __init__(self, repo: MatchRepository):
        self._repo = repo

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
