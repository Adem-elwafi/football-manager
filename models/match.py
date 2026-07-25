from dataclasses import dataclass


@dataclass
class Match:
    id: int
    date_time: str
    stadium_cost: float = 42.0
    transport_cost: float = 30.0
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            date_time=row["date_time"],
            stadium_cost=row["stadium_cost"],
            transport_cost=row["transport_cost"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
