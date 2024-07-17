import datetime
from typing import Any

from pydantic import BaseModel


class SAddResult(BaseModel):
    ok: bool = True
    new_id: int
    created: datetime.datetime


class SDeleteResult(BaseModel):
    ok: bool = True
    was_deleted: bool


class SUpdateResult(BaseModel):
    ok: bool = True
    updated: datetime.datetime
    data: Any


class SQueryResult(BaseModel):
    count: int
    data: list[Any]
