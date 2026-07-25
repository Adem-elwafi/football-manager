from typing import Optional
from dataclasses import dataclass


@dataclass
class Player:
    id: int
    name: str
    phone: str
    is_archived: bool = False
    created_at: str = ""

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            phone=row["phone"],
            is_archived=bool(row["is_archived"]),
            created_at=row["created_at"],
        )


@dataclass
class PlayerStats:
    player_id: int
    matches_played: int = 0
    attendance_rate: float = 0.0
    last_participation: Optional[str] = None
    total_paid: float = 0.0
    total_owed: float = 0.0
