from pydantic import BaseModel


class SCustomerAdd(BaseModel):
    name: str


class SCustomer(SCustomerAdd):
    id: int


class AddedResult(BaseModel):
    ok: bool = True
    new_id: int
