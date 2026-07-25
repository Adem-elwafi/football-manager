from dataclasses import dataclass


@dataclass
class Expense:
    id: int
    match_id: int
    description: str
    amount: float

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            match_id=row["match_id"],
            description=row["description"],
            amount=row["amount"],
        )
