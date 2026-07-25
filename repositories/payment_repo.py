from typing import Optional
from models.payment import Payment


class PaymentRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, match_id: int, player_id: int, amount: float) -> Payment:
        cur = self._conn.execute(
            "INSERT INTO payments (match_id, player_id, amount) VALUES (?, ?, ?)",
            (match_id, player_id, amount),
        )
        return Payment(
            id=cur.lastrowid,
            match_id=match_id,
            player_id=player_id,
            amount=amount,
        )

    def get_by_match(self, match_id: int) -> list[Payment]:
        cur = self._conn.execute(
            "SELECT * FROM payments WHERE match_id = ? ORDER BY paid_at", (match_id,)
        )
        return [Payment.from_row(r) for r in cur.fetchall()]

    def get_by_player_and_match(self, match_id: int, player_id: int) -> list[Payment]:
        cur = self._conn.execute(
            "SELECT * FROM payments WHERE match_id = ? AND player_id = ? ORDER BY paid_at",
            (match_id, player_id),
        )
        return [Payment.from_row(r) for r in cur.fetchall()]

    def total_by_match(self, match_id: int) -> float:
        cur = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE match_id = ?",
            (match_id,),
        )
        return cur.fetchone()["total"]

    def total_by_player_and_match(self, match_id: int, player_id: int) -> float:
        cur = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE match_id = ? AND player_id = ?",
            (match_id, player_id),
        )
        return cur.fetchone()["total"]

    def total_by_player(self, player_id: int) -> float:
        cur = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE player_id = ?",
            (player_id,),
        )
        return cur.fetchone()["total"]

    def delete_by_match(self, match_id: int) -> None:
        self._conn.execute("DELETE FROM payments WHERE match_id = ?", (match_id,))

    def delete_by_player(self, player_id: int) -> None:
        self._conn.execute("DELETE FROM payments WHERE player_id = ?", (player_id,))
