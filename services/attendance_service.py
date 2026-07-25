from typing import List
from models.player import Player
from repositories.attendance_repo import AttendanceRepository
from repositories.player_repo import PlayerRepository


class AttendanceService:
    def __init__(self, attendance_repo: AttendanceRepository, player_repo: PlayerRepository):
        self._attendance_repo = attendance_repo
        self._player_repo = player_repo

    def set_attendance(self, match_id: int, player_id: int, is_attending: bool) -> None:
        self._attendance_repo.set_attendance(match_id, player_id, is_attending)

    def get_attendees(self, match_id: int) -> List[Player]:
        player_ids = self._attendance_repo.get_player_ids_by_match(match_id)
        players = []
        for pid in player_ids:
            p = self._player_repo.get_by_id(pid)
            if p:
                players.append(p)
        return players

    def get_attendance_count(self, match_id: int) -> int:
        return self._attendance_repo.get_count_by_match(match_id)
