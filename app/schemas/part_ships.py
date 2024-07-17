import datetime

from pydantic import BaseModel


class SPartShipAdd(BaseModel):
    date: datetime.date
    place_count: int
    weight: int
    volume: float


class SPartShip(SPartShipAdd):
    id: int
