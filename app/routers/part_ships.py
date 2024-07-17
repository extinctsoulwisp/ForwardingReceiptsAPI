from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionM, ReceiptORM, PartShipORM
from app.schemas import SAddResult, SDeleteResult
from app.schemas.part_ships import SPartShip, SPartShipAdd

router = APIRouter(
    prefix='/receipts/{receipt_id}/part-ships',
    tags=["Part Ships"]
)


@router.get('/')
async def get_part_ships(receipt_id: int) -> list[SPartShip]:
    async with AsyncSessionM() as session:
        query = (select(ReceiptORM).options(selectinload(ReceiptORM.part_ships_r))
                 .filter(ReceiptORM.id == receipt_id))
        result = await session.execute(query)

        if (receipt := result.scalars().first()) is None:
            raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

        else:
            return [SPartShip(
                id=part_ship.id,
                date=part_ship.date,
                place_count=part_ship.place_count,
                volume=part_ship.volume,
                weight=part_ship.weight
            ) for part_ship in receipt.part_ships_r]


@router.post('/')
async def add_part_ship(receipt_id: int, part_ship: Annotated[SPartShipAdd, Depends()]) -> SAddResult:
    async with AsyncSessionM() as session:
        query = (select(ReceiptORM).options(selectinload(ReceiptORM.part_ships_r))
                 .filter(ReceiptORM.id == receipt_id))
        result = await session.execute(query)

        if (receipt := result.scalars().first()) is None:
            raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

        else:
            receipt.part_ships_r.append(new_part_ship := PartShipORM(
                date=part_ship.date,
                place_count=part_ship.place_count,
                weight=part_ship.weight,
                volume=part_ship.volume
            ))

            receipt.place_count -= part_ship.place_count
            receipt.volume -= part_ship.volume
            receipt.weight -= part_ship.weight

            await session.flush()
            await session.commit()

            return SAddResult(new_id=new_part_ship.id, created=new_part_ship.created_at)


@router.delete('/{part_ship_id}')
async def delete_part_ship(receipt_id: int, part_ship_id: int) -> SDeleteResult:
    async with AsyncSessionM() as session:
        query = (select(ReceiptORM).filter(ReceiptORM.id == receipt_id))
        result = await session.execute(query)

        if (result.scalars().first()) is None:
            raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

        query = (select(PartShipORM).filter(PartShipORM.id == part_ship_id))
        result = await session.execute(query)

        if (part_ship := result.scalars().first()) is None:
            return SDeleteResult(was_deleted=False)

        else:
            await session.delete(part_ship)
            await session.commit()

            return SDeleteResult(was_deleted=True)
