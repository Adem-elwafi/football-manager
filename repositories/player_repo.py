from typing import Optional
from models.player import Player


class PlayerRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, name: str, phone: str) -> Player:
        cur = self._conn.execute(
            "INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone)
        )
        return self.get_by_id(cur.lastrowid)

    def get_by_id(self, player_id: int) -> Optional[Player]:
        cur = self._conn.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        return Player.from_row(cur.fetchone())

    def get_all(self, include_archived: bool = False) -> list[Player]:
        if include_archived:
            cur = self._conn.execute("SELECT * FROM players ORDER BY name")
        else:
            cur = self._conn.execute(
                "SELECT * FROM players WHERE is_archived = 0 ORDER BY name"
            )
        return [Player.from_row(r) for r in cur.fetchall()]

    def search(self, query: str, include_archived: bool = False) -> list[Player]:
        q = f"%{query}%"
        if include_archived:
            cur = self._conn.execute(
                "SELECT * FROM players WHERE (name LIKE ? OR phone LIKE ?) ORDER BY name",
                (q, q),
            )
        else:
            cur = self._conn.execute(
                "SELECT * FROM players WHERE (name LIKE ? OR phone LIKE ?) AND is_archived = 0 ORDER BY name",
                (q, q),
            )
        return [Player.from_row(r) for r in cur.fetchall()]

    def archive(self, player_id: int) -> None:
        self._conn.execute(
            "UPDATE players SET is_archived = 1 WHERE id = ?", (player_id,)
        )

    def unarchive(self, player_id: int) -> None:
        self._conn.execute(
            "UPDATE players SET is_archived = 0 WHERE id = ?", (player_id,)
        )

    def delete(self, player_id: int) -> None:
        self._conn.execute("DELETE FROM players WHERE id = ?", (player_id,))
