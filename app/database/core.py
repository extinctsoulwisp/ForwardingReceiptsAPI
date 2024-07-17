from sqlalchemy import Table, Column, ForeignKey, select, BinaryExpression, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped

from app.config import get_db_url
from . import int_pk, created_at, updated_at

DATABASE_URL = get_db_url()

engine = create_async_engine(DATABASE_URL)
AsyncSessionM = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        return self.__name__

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


def secondary_table(parent: str, children: type[Base]) -> Table:
    return Table(
        f"_association_{parent.lower()}_{children.__name__.lower()}",
        Base.metadata,
        Column("left_id", ForeignKey(parent + '.id')),
        Column("right_id", ForeignKey(children.id)),
    )


async def get_if_exist(instance: Base, *attrs: Column, async_session: AsyncSession):
    stmt = (
        select(type(instance))
        .filter(*(attr == getattr(instance, attr.key) for attr in attrs))
        .limit(1)
    )
    result = await async_session.execute(stmt)
    if (new_instance := result.scalars().first()) is not None:
        return new_instance
    else:
        return instance


async def get_count(model: type[Base], *filters: BinaryExpression, async_session: AsyncSession) -> int:
    stmt = (select(func.count(model.id)).filter(*filters))
    result = await async_session.execute(stmt)
    return result.scalars().one()
