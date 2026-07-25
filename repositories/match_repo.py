from typing import Optional
from models.match import Match


class MatchRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, date_time: str, stadium_cost: float, transport_cost: float) -> Match:
        cur = self._conn.execute(
            "INSERT INTO matches (date_time, stadium_cost, transport_cost) VALUES (?, ?, ?)",
            (date_time, stadium_cost, transport_cost),
        )
        return self.get_by_id(cur.lastrowid)

    def get_by_id(self, match_id: int) -> Optional[Match]:
        cur = self._conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
        return Match.from_row(cur.fetchone())

    def get_all(self, limit: int = 50) -> list[Match]:
        cur = self._conn.execute(
            "SELECT * FROM matches ORDER BY date_time DESC LIMIT ?", (limit,)
        )
        return [Match.from_row(r) for r in cur.fetchall()]

    def get_latest(self) -> Optional[Match]:
        return self.get_all(limit=1)[0] if self.get_all(limit=1) else None

    def update(self, match_id: int, **fields) -> Optional[Match]:
        allowed = {"date_time", "stadium_cost", "transport_cost", "notes"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_by_id(match_id)
        updates["updated_at"] = "datetime('now', 'localtime')"
        set_clause = ", ".join(f"{k} = ?" for k in updates if k != "updated_at")
        set_clause += ", updated_at = datetime('now', 'localtime')"
        values = [updates[k] for k in updates if k != "updated_at"]
        values.append(match_id)
        self._conn.execute(
            f"UPDATE matches SET {set_clause} WHERE id = ?", values
        )
        return self.get_by_id(match_id)

    def delete(self, match_id: int) -> None:
        self._conn.execute("DELETE FROM matches WHERE id = ?", (match_id,))
