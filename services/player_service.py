from typing import Optional, List
from models.player import Player, PlayerStats
from repositories.player_repo import PlayerRepository


class PlayerService:
    def __init__(self, repo: PlayerRepository):
        self._repo = repo

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
        return PlayerStats(player_id=player_id)
