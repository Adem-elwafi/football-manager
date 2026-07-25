from dataclasses import dataclass


@dataclass
class TeamAssignment:
    id: int
    match_id: int
    player_id: int
    team: int
    is_locked: bool = False

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            match_id=row["match_id"],
            player_id=row["player_id"],
            team=row["team"],
            is_locked=bool(row["is_locked"]),
        )
