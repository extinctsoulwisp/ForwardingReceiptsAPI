from pydantic import BaseModel


class SGetCrateResult(BaseModel):
    exist: bool = True
    old_wight: int | None = None
    old_volume: float | None = None


class SSetCrate(BaseModel):
    new_wight: int
    new_volume: float
