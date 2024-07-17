from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.database import AsyncSession, CustomerORM
from app.schemas import SCustomerAdd, SCustomer, AddedResult

router = APIRouter(
    prefix='/customers',
    tags=["Customers"]
)


@router.get('/')
async def get_tasks() -> list[SCustomer]:
    async with AsyncSession() as session:
        query = select(CustomerORM)
        result = await session.execute(query)
        models = result.scalars().all()
        schemas = [SCustomer.model_validate(model) for model in models]
        return schemas


@router.post('/add')
async def add_task(customer: Annotated[SCustomerAdd, Depends()]) -> AddedResult:
    async with AsyncSession() as session:
        customer_orm = CustomerORM(**customer.model_dump())
        session.add(customer_orm)

        await session.flush()
        await session.commit()

        return AddedResult(new_id=customer_orm.id)
