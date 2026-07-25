from datetime import datetime, timedelta


def get_next_saturday_2030():
    now = datetime.now()
    days_ahead = 5 - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_sat = now + timedelta(days=days_ahead)
    return next_sat.replace(hour=20, minute=30, second=0, microsecond=0)
