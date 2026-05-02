from datetime import datetime, timezone
from typing import Any, Annotated
from pydantic import BeforeValidator, PlainSerializer
from neo4j.time import DateTime as Neo4jDateTime


def validate_timestamp(v: Any) -> datetime:
    if isinstance(v, Neo4jDateTime):
        return datetime(
            v.year,
            v.month,
            v.day,
            v.hour,
            v.minute,
            v.second,
            v.nanosecond // 1000,
            tzinfo=timezone.utc,
        )
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, tz=timezone.utc)
    if isinstance(v, datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
    return v


UnixTimestamp = Annotated[
    datetime,
    BeforeValidator(validate_timestamp),
    PlainSerializer(lambda dt: int(dt.timestamp()), return_type=int),
]
