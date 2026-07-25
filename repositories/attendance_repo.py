from typing import Optional
from typing import Optional
from models.attendance import Attendance


class AttendanceRepository:
    def __init__(self, conn):
        self._conn = conn

    def set_attendance(self, match_id: int, player_id: int, is_attending: bool) -> None:
        if is_attending:
            self._conn.execute(
                "INSERT OR IGNORE INTO attendance (match_id, player_id) VALUES (?, ?)",
                (match_id, player_id),
            )
        else:
            self._conn.execute(
                "DELETE FROM attendance WHERE match_id = ? AND player_id = ?",
                (match_id, player_id),
            )

    def get_by_match(self, match_id: int) -> list[Attendance]:
        cur = self._conn.execute(
            "SELECT * FROM attendance WHERE match_id = ?", (match_id,)
        )
        return [Attendance.from_row(r) for r in cur.fetchall()]

    def get_player_ids_by_match(self, match_id: int) -> list[int]:
        cur = self._conn.execute(
            "SELECT player_id FROM attendance WHERE match_id = ?", (match_id,)
        )
        return [r["player_id"] for r in cur.fetchall()]

    def get_count_by_match(self, match_id: int) -> int:
        cur = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM attendance WHERE match_id = ?", (match_id,)
        )
        return cur.fetchone()["cnt"]

    def delete_by_match(self, match_id: int) -> None:
        self._conn.execute("DELETE FROM attendance WHERE match_id = ?", (match_id,))

    def get_count_by_player(self, player_id: int) -> int:
        cur = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM attendance WHERE player_id = ?", (player_id,)
        )
        return cur.fetchone()["cnt"]

    def get_last_match_date(self, player_id: int) -> Optional[str]:
        cur = self._conn.execute(
            "SELECT m.date_time FROM attendance a JOIN matches m ON a.match_id = m.id "
            "WHERE a.player_id = ? ORDER BY m.date_time DESC LIMIT 1",
            (player_id,),
        )
        row = cur.fetchone()
        return row["date_time"] if row else None

    def get_match_ids_by_player(self, player_id: int) -> list[int]:
        cur = self._conn.execute(
            "SELECT match_id FROM attendance WHERE player_id = ?", (player_id,)
        )
        return [r["match_id"] for r in cur.fetchall()]

    def delete_by_player(self, player_id: int) -> None:
        self._conn.execute(
            "DELETE FROM attendance WHERE player_id = ?", (player_id,)
        )
