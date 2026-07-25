from abc import ABC, abstractmethod
from typing import List, Tuple
from repositories.team_repo import TeamRepository
from repositories.attendance_repo import AttendanceRepository
from repositories.player_repo import PlayerRepository


class BaseTeamBalancer(ABC):
    @abstractmethod
    def balance(self, players: List[str]) -> Tuple[List[str], Tuple[List[str], List[str]]]:
        ...


class RandomBalancer(BaseTeamBalancer):
    def balance(self, players: List[str]) -> Tuple[List[str], List[str]]:
        import random
        shuffled = players.copy()
        random.shuffle(shuffled)
        mid = len(shuffled) // 2
        return shuffled[:mid], shuffled[mid:]


class TeamService:
    def __init__(
        self,
        team_repo: TeamRepository,
        attendance_repo: AttendanceRepository,
        player_repo: PlayerRepository,
    ):
        self._team_repo = team_repo
        self._attendance_repo = attendance_repo
        self._player_repo = player_repo

    def _attendee_names(self, match_id: int) -> List[str]:
        player_ids = self._attendance_repo.get_player_ids_by_match(match_id)
        names = []
        for pid in player_ids:
            p = self._player_repo.get_by_id(pid)
            if p:
                names.append(p.name)
        return names

    def generate_teams(
        self, match_id: int, balancer: BaseTeamBalancer = None
    ) -> Tuple[List[str], List[str]]:
        if balancer is None:
            balancer = RandomBalancer()
        names = self._attendee_names(match_id)
        if len(names) < 2:
            return [], []
        team_a, team_b = balancer.balance(names)
        self._team_repo.delete_by_match(match_id)
        for p in team_a:
            player = self._player_repo.search(p)
            if player:
                self._team_repo.set_team(match_id, player[0].id, 0)
        for p in team_b:
            player = self._player_repo.search(p)
            if player:
                self._team_repo.set_team(match_id, player[0].id, 1)
        return team_a, team_b

    def reshuffle_teams(
        self, match_id: int, balancer: BaseTeamBalancer = None
    ) -> Tuple[List[str], List[str]]:
        if balancer is None:
            balancer = RandomBalancer()
        player_ids = self._attendance_repo.get_player_ids_by_match(match_id)
        locked = self._team_repo.get_locked_by_match(match_id)
        locked_ids = {a.player_id for a in locked}
        unlocked_ids = [pid for pid in player_ids if pid not in locked_ids]

        unlocked_names = []
        for pid in unlocked_ids:
            p = self._player_repo.get_by_id(pid)
            if p:
                unlocked_names.append(p.name)

        if len(unlocked_names) < 2:
            return self._get_team_names(match_id)

        fresh_a, fresh_b = balancer.balance(unlocked_names)
        self._team_repo.delete_by_match(match_id)
        current_team = 0
        for name in fresh_a:
            players = self._player_repo.search(name)
            if players:
                self._team_repo.set_team(match_id, players[0].id, 0)
                current_team = 0
        for name in fresh_b:
            players = self._player_repo.search(name)
            if players:
                self._team_repo.set_team(match_id, players[0].id, 1)

        for ta in locked:
            self._team_repo.set_team(match_id, ta.player_id, ta.team)
            self._team_repo.set_locked(match_id, ta.player_id, True)

        return self._get_team_names(match_id)

    def lock_player(self, match_id: int, player_id: int) -> None:
        self._team_repo.set_locked(match_id, player_id, True)

    def unlock_player(self, match_id: int, player_id: int) -> None:
        self._team_repo.set_locked(match_id, player_id, False)

    def _get_team_names(self, match_id: int) -> Tuple[List[str], List[str]]:
        assignments = self._team_repo.get_by_match(match_id)
        team_a, team_b = [], []
        for a in assignments:
            p = self._player_repo.get_by_id(a.player_id)
            name = p.name if p else f"Player #{a.player_id}"
            if a.team == 0:
                team_a.append(name)
            else:
                team_b.append(name)
        return team_a, team_b
