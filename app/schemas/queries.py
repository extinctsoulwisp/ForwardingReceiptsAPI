import enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Column

from app.database import Base


class SGetQueryOperation(enum.Enum):
    # all
    equality = 'equality'

    # numbers, dates
    less = 'less'
    greater = 'greater'

    # strs
    like = 'like'
    startswith = 'startswith'
    endswith = 'endswith'


class SGetQueryFilter(BaseModel):
    attr: str
    operation: SGetQueryOperation
    use_not: bool = False
    target: Any


class SGetQueryOrder(BaseModel):
    attr: str
    use_asc: bool = True


class SGetQuery(BaseModel):
    limit: int = 1
    offset: int = 0

    filters: list[SGetQueryFilter] = []
    orders: list[SGetQueryOrder] = []


def get_sqlalchemy_filter(orm: type[Base], q_filter: SGetQueryFilter):
    column: Column = getattr(orm, q_filter.attr)
    match q_filter.operation:
        
        case SGetQueryOperation.equality:
            return column != q_filter.target if q_filter.use_not else column == q_filter.target
         
        case SGetQueryOperation.less:
            return column >= q_filter.target if q_filter.use_not else column < q_filter.target
        
        case SGetQueryOperation.greater:
            return column <= q_filter.target if q_filter.use_not else column > q_filter.target
        
        case SGetQueryOperation.like:
            return column.notilike(f'%{q_filter.target}%') if q_filter.use_not else column.ilike(f'%{q_filter.target}%')
        
        case SGetQueryOperation.startswith:
            return not column.istartswith(q_filter.target) if q_filter.use_not else column.istartswith(q_filter.target)

        case SGetQueryOperation.endswith:
            return not column.iendswith(q_filter.target) if q_filter.use_not else column.iendswith(q_filter.target)


def get_sqlalchemy_order(orm: type[Base], q_order: SGetQueryOrder):
    column: Column = getattr(orm, q_order.attr)
    return column.asc() if q_order.use_asc else column.desc()
