from models.expense import Expense


class ExpenseRepository:
    def __init__(self, conn):
        self._conn = conn

    def add(self, match_id: int, description: str, amount: float) -> Expense:
        cur = self._conn.execute(
            "INSERT INTO expenses (match_id, description, amount) VALUES (?, ?, ?)",
            (match_id, description, amount),
        )
        return Expense(id=cur.lastrowid, match_id=match_id, description=description, amount=amount)

    def get_by_match(self, match_id: int) -> list[Expense]:
        cur = self._conn.execute(
            "SELECT * FROM expenses WHERE match_id = ? ORDER BY id", (match_id,)
        )
        return [Expense.from_row(r) for r in cur.fetchall()]

    def total_by_match(self, match_id: int) -> float:
        cur = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE match_id = ?",
            (match_id,),
        )
        return cur.fetchone()["total"]

    def delete(self, expense_id: int) -> None:
        self._conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    def delete_by_match(self, match_id: int) -> None:
        self._conn.execute("DELETE FROM expenses WHERE match_id = ?", (match_id,))
