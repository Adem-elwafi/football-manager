from models.team_assignment import TeamAssignment


class TeamRepository:
    def __init__(self, conn):
        self._conn = conn

    def set_team(self, match_id: int, player_id: int, team: int) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO team_assignments (match_id, player_id, team, is_locked) "
            "VALUES (?, ?, ?, COALESCE((SELECT is_locked FROM team_assignments WHERE match_id = ? AND player_id = ?), 0))",
            (match_id, player_id, team, match_id, player_id),
        )

    def set_locked(self, match_id: int, player_id: int, is_locked: bool) -> None:
        self._conn.execute(
            "UPDATE team_assignments SET is_locked = ? WHERE match_id = ? AND player_id = ?",
            (int(is_locked), match_id, player_id),
        )

    def get_by_match(self, match_id: int) -> list[TeamAssignment]:
        cur = self._conn.execute(
            "SELECT * FROM team_assignments WHERE match_id = ? ORDER BY team, player_id",
            (match_id,),
        )
        return [TeamAssignment.from_row(r) for r in cur.fetchall()]

    def get_locked_by_match(self, match_id: int) -> list[TeamAssignment]:
        cur = self._conn.execute(
            "SELECT * FROM team_assignments WHERE match_id = ? AND is_locked = 1",
            (match_id,),
        )
        return [TeamAssignment.from_row(r) for r in cur.fetchall()]

    def delete_by_match(self, match_id: int) -> None:
        self._conn.execute("DELETE FROM team_assignments WHERE match_id = ?", (match_id,))

    def delete_by_player(self, player_id: int) -> None:
        self._conn.execute(
            "DELETE FROM team_assignments WHERE player_id = ?", (player_id,)
        )
