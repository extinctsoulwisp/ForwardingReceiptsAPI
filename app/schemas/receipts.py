import datetime

from pydantic import BaseModel

from app.schemas import SQueryResult, SUpdateResult


class SReceiptAdd(BaseModel):
    city: str
    shipper: str
    consignee: str
    customer: str
    forwarder: str
    shipper_fullname: str
    container: str
    doc: str
    address: str
    shipper_phone: str
    consignee_phone: str
    product: str
    place_count: int
    weight: int
    volume: float
    price: float
    product_code: str

    in_nsk: bool
    add_container: bool
    special_options: list[str] = []
    comment: str | None = None


class SReceipt(SReceiptAdd):
    id: int
    created: datetime.datetime
    updated: datetime.datetime

    forwarder_name: str | None
    carriage_number: int | None
    status: str
    date_of_load: datetime.date | None


class SReceiptQueryResult(SQueryResult):
    data: list[SReceipt]


class SReceiptEdit(BaseModel):
    city: str | None = None
    shipper: str | None = None
    consignee: str | None = None
    customer: str | None = None
    forwarder_com_name: str | None = None
    shipper_fullname: str | None = None
    container: str | None = None
    doc: str | None = None
    address: str | None = None
    shipper_phone: str | None = None
    consignee_phone: str | None = None
    product: str | None = None
    place_count: int | None = None
    weight: int | None = None
    volume: float | None = None
    price: float | None = None
    product_code: str | None = None
    in_nsk: bool | None = None
    add_container: bool | None = None
    special_options: list[str] | None = None
    comment: str | None = None
    carriage_number: int | None = None
    status: str | None = None
    date_of_load: datetime.date | None = None


class SReceiptUpdateResult(SUpdateResult):
    data: SReceipt
