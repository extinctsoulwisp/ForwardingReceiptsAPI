import enum
import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, Enum, DATE
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, str_null_false, smallint_null_true, secondary_table, float_null_false, \
    smallint_null_false, bool_null_false, date_null_true, str_null_true, int_pk


class ForwarderORM(Base):
    com_name: Mapped[str] = mapped_column(primary_key=True)

    name: Mapped[str_null_false]
    phone: Mapped[str_null_false]
    address: Mapped[str_null_false]
    site: Mapped[str_null_false]


class SpecialOptionORM(Base):
    id: Mapped[int_pk]

    name: Mapped[str_null_false]
    ordered: Mapped[smallint_null_true]


class CityORM(Base):
    name: Mapped[str] = mapped_column(primary_key=True)
    partner_name: Mapped[str_null_false]
    partner_address: Mapped[str_null_false]
    partner_phone: Mapped[str_null_false]
    is_paid_entry: Mapped[bool_null_false]


class StatusEnum(enum.Enum):
    in_stock = 0
    shipped = 1
    refund = 2


StatusEnumORM = Enum(StatusEnum)
SpecialOptionReceiptORM = secondary_table("ReceiptORM", SpecialOptionORM)


class CrateORM(Base):
    receipt_id: Mapped[Annotated[int, mapped_column(ForeignKey('ReceiptORM.id'), primary_key=True)]]
    old_weight: Mapped[smallint_null_false]
    old_volume: Mapped[smallint_null_false]


class PartShipORM(Base):
    id: Mapped[int_pk]

    receipt_id: Mapped[Annotated[int, mapped_column(ForeignKey('ReceiptORM.id'))]]
    date: Mapped[Annotated[datetime.date, mapped_column(DATE, nullable=False)]]
    place_count: Mapped[smallint_null_false]
    weight: Mapped[smallint_null_false]
    volume: Mapped[float_null_false]


class ReceiptORM(Base):
    id: Mapped[int_pk]

    price: Mapped[float_null_false]
    place_count: Mapped[smallint_null_false]
    weight: Mapped[smallint_null_false]
    volume: Mapped[float_null_false]
    product_code: Mapped[str_null_false]
    doc: Mapped[str_null_false]
    address: Mapped[str_null_false]
    in_nsk: Mapped[bool_null_false]
    shipper_fullname: Mapped[str_null_false]
    is_add_container: Mapped[bool_null_false]

    status: Mapped[Annotated[StatusEnum, mapped_column(StatusEnumORM, default=StatusEnum.in_stock)]]
    carriage_number: Mapped[smallint_null_true]
    date_of_load: Mapped[date_null_true]

    shipper: Mapped[str_null_false]
    shipper_phone: Mapped[str_null_false]
    consignee: Mapped[str_null_false]
    consignee_phone: Mapped[str_null_false]
    customer: Mapped[str_null_false]
    container: Mapped[str_null_false]
    product: Mapped[str_null_false]
    comment: Mapped[str_null_true]

    city: Mapped[str] = mapped_column(ForeignKey(CityORM.name))
    forwarder: Mapped[str] = mapped_column(ForeignKey(ForwarderORM.com_name))

    crate_r: Mapped[CrateORM] = relationship(CrateORM, foreign_keys=[CrateORM.receipt_id], uselist=False)
    part_ships_r: Mapped[list[PartShipORM]] = relationship(PartShipORM, foreign_keys=[PartShipORM.receipt_id], uselist=True)
    special_options_r: Mapped[list[SpecialOptionORM]] = relationship(secondary=SpecialOptionReceiptORM, uselist=True)
    city_r: Mapped[CityORM] = relationship(CityORM, foreign_keys=[city], uselist=False)
    forwarder_r: Mapped[ForwarderORM] = relationship(ForwarderORM, foreign_keys=[forwarder], uselist=False)


class AttorneyORM(Base):
    id: Mapped[int_pk]

    number: Mapped[smallint_null_true]
    com_name: Mapped[smallint_null_false]
    partner_name: Mapped[str_null_false]
    started: Mapped[date_null_true]
    finished: Mapped[date_null_true]
    passport: Mapped[str_null_false]
    permission: Mapped[str_null_false]


class CeilColorORM(Base):
    id: Mapped[int_pk]

    tablename: Mapped[str_null_false]
    column_name: Mapped[str_null_false]
    row_id: Mapped[int]
    _color: Mapped[int]

    @property
    def color(self) -> tuple[int, int, int]:
        int_color = self._color
        c = (int_color // 1_000_000, int_color // 1_000 % 1_000, int_color % 1_000)
        return c

    @color.setter
    def color(self, value: tuple[int, int, int]):
        # noinspection PyTypeChecker
        self._color = value[0] + 1_000 * value[1] + 1_000_000 * value[2]
