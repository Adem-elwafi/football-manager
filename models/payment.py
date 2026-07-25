from dataclasses import dataclass


@dataclass
class Payment:
    id: int
    match_id: int
    player_id: int
    amount: float
    paid_at: str = ""

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            match_id=row["match_id"],
            player_id=row["player_id"],
            amount=row["amount"],
            paid_at=row["paid_at"],
        )
