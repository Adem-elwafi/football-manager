def format_currency(amount: float) -> str:
    return f"{amount:.2f} DT"


def format_date(date_str: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%a, %d %b %Y — %H:%M")
    except (ValueError, TypeError):
        return date_str
