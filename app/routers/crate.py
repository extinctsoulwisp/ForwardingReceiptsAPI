from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionM, CrateORM, ReceiptORM
from app.schemas import SGetCrateResult, SAddResult, SSetCrate, SDeleteResult

router = APIRouter(
    prefix='/receipts/{receipt_id}/crate',
    tags=["Crate"]
)


@router.get('/')
async def get_crate(receipt_id: int) -> SGetCrateResult:
    async with AsyncSessionM() as session:
        query = (select(ReceiptORM).options(selectinload(ReceiptORM.crate_r))
                 .filter(ReceiptORM.id == receipt_id))
        result = await session.execute(query)

        if (receipt := result.scalars().first()) is None:
            raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

        elif receipt.crate_r is None:
            return SGetCrateResult(exist=False)

        else:
            return SGetCrateResult(old_wight=receipt.crate_r.old_weight, old_volume=receipt.crate_r.old_volume)


@router.post('/')
async def set_crate(receipt_id: int, crate: Annotated[SSetCrate, Depends()]) -> SAddResult:
    async with AsyncSessionM() as session:
        query = (select(ReceiptORM).options(selectinload(ReceiptORM.crate_r))
                 .filter(ReceiptORM.id == receipt_id))
        result = await session.execute(query)

        if (receipt := result.scalars().first()) is None:
            raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

        else:
            receipt: ReceiptORM
            if receipt.crate_r is None:
                receipt.crate_r = CrateORM(old_volume=receipt.volume, old_weight=receipt.weight)

            receipt.volume = crate.new_volume
            receipt.weight = crate.new_wight

            await session.flush()
            await session.commit()

        return SAddResult(new_id=receipt.crate_r.receipt_id, created=receipt.crate_r.created_at)


@router.delete('/')
async def delete_crate(receipt_id: int) -> SDeleteResult:
    async with AsyncSessionM() as session:
        query = (select(CrateORM).filter(CrateORM.receipt_id == receipt_id))
        result = await session.execute(query)

        if (crate := result.scalars().first()) is None:
            return SDeleteResult(was_deleted=False)

        else:
            await session.delete(crate)
            await session.commit()
            return SDeleteResult(was_deleted=True)
        