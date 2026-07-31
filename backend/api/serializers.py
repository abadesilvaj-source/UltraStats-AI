from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo


def iso_local(value: datetime | None, tz_name: str) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(ZoneInfo(tz_name)).isoformat()


def json_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value
