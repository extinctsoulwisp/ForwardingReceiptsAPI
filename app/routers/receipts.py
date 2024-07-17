from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.responses import FileResponse

from app.database import AsyncSessionM, ReceiptORM, CityORM, SpecialOptionORM, ForwarderORM
from app.database.core import get_if_exist, get_count
from app.schemas import SReceipt, SGetQuery, get_sqlalchemy_filter, get_sqlalchemy_order, SReceiptAdd, SAddResult, \
    SReceiptQueryResult, SGetQueryFilter, SGetQueryOperation, SReceiptUpdateResult, SReceiptEdit
from services.documents.receipt import create_receipt_doc

router = APIRouter(
    prefix='/receipts',
    tags=["Receipts"]
)


@router.post('/query')
async def get_receipts(query: Annotated[SGetQuery, Depends()]) -> SReceiptQueryResult:
    async with AsyncSessionM() as session:
        query = (
            select(ReceiptORM)
            .options(
                selectinload(ReceiptORM.city_r),
                selectinload(ReceiptORM.special_options_r),
                selectinload(ReceiptORM.forwarder_r),
            )
            .filter(*(filters := [get_sqlalchemy_filter(ReceiptORM, q_filter) for q_filter in query.filters]))
            .order_by(*(get_sqlalchemy_order(ReceiptORM, q_order) for q_order in query.orders))
            .limit(query.limit).offset(query.offset)
        )
        result = await session.execute(query)
        models = result.scalars().all()
        schemas = [
            SReceipt(
                city=model.city,
                shipper=model.shipper,
                consignee=model.consignee,
                customer=model.customer,
                forwarder=model.forwarder,
                weight=model.weight,
                volume=model.volume,
                shipper_fullname=model.shipper_fullname,
                special_options=[option.name for option in model.special_options_r],
                status=model.status,
                shipper_phone=model.shipper_phone,
                address=model.address,
                add_container=model.is_add_container,
                carriage_number=model.carriage_number,
                comment=model.comment,
                consignee_phone=model.consignee_phone,
                created=model.created_at,
                container=model.container,
                date_of_load=model.date_of_load,
                doc=model.doc,
                forwarder_name=model.forwarder_r.name,
                id=model.id,
                in_nsk=model.in_nsk,
                product_code=model.product_code,
                place_count=model.place_count,
                price=model.price,
                product=model.product,
                updated=model.updated_at
            ) for model in models
        ]
        count = await get_count(ReceiptORM, *filters, async_session=session)
        return SReceiptQueryResult(count=count, data=schemas)


@router.post('/')
async def add_receipt(receipt: Annotated[SReceiptAdd, Depends()]) -> SAddResult:
    async with AsyncSessionM() as session:
        city: CityORM = await get_if_exist(
            CityORM(name=receipt.city, partner_name="", partner_address="", partner_phone="", is_paid_entry=False),
            CityORM.name,
            async_session=session
        )
        forwarder: ForwarderORM = await get_if_exist(
            ForwarderORM(com_name=receipt.forwarder),
            ForwarderORM.com_name,
            async_session=session
        )
        special_options = [
            await get_if_exist(
                SpecialOptionORM(name=option, ordered=None),
                SpecialOptionORM.name,
                async_session=session
            ) for option in receipt.special_options
        ]

        session.add(new_receipt := ReceiptORM(
            price=receipt.price,
            place_count=receipt.place_count,
            weight=receipt.weight,
            volume=receipt.volume,
            product_code=receipt.product_code,
            doc=receipt.doc,
            address=receipt.address,
            in_nsk=receipt.in_nsk,
            shipper_fullname=receipt.shipper_fullname,
            is_add_container=receipt.add_container,
            shipper=receipt.shipper,
            shipper_phone=receipt.shipper_phone,
            consignee=receipt.consignee,
            consignee_phone=receipt.consignee_phone,
            product=receipt.product,
            customer=receipt.customer,
            container=receipt.container,

            forwarder_r=forwarder,
            city_r=city,
            special_options_r=special_options
        ))

        await session.flush()
        await session.commit()

        return SAddResult(new_id=new_receipt.id, created=new_receipt.created_at)


@router.get('/{receipt_id}')
async def get_receipt(receipt_id: int) -> SReceipt:
    result = await get_receipts(SGetQuery(filters=[
        SGetQueryFilter(attr="id", operation=SGetQueryOperation.equality, target=receipt_id)
    ]))

    if not result.data:
        raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

    else:
        return result.data[0]


@router.patch('/{receipt_id}')
async def edit_receipt(receipt_id: int, edited: Annotated[SReceiptEdit, Depends()]) -> SReceiptUpdateResult:
    async with AsyncSessionM() as session:
        query = (
            select(ReceiptORM)
            .options(
                selectinload(ReceiptORM.crate_r),
                selectinload(ReceiptORM.forwarder_r),
                selectinload(ReceiptORM.special_options_r)
            )
            .filter(ReceiptORM.id == receipt_id)
        )
        result = await session.execute(query)

        if (receipt := result.scalars().first()) is None:
            raise HTTPException(status_code=404, detail=f"Receipt with id={receipt_id} not found")

        if edited.shipper: receipt.shipper = edited.shipper
        if edited.consignee: receipt.consignee = edited.consignee
        if edited.customer: receipt.customer = edited.customer
        if edited.shipper_fullname: receipt.shipper_fullname = edited.shipper_fullname
        if edited.container: receipt.container = edited.container
        if edited.doc: receipt.doc = edited.doc
        if edited.address: receipt.address = edited.address
        if edited.shipper_phone: receipt.shipper_phone = edited.shipper_phone
        if edited.consignee_phone: receipt.consignee_phone = edited.consignee_phone
        if edited.product: receipt.product = edited.product
        if edited.place_count: receipt.place_count = edited.place_count
        if edited.weight: receipt.weight = edited.weight
        if edited.volume: receipt.volume = edited.volume
        if edited.price: receipt.price = edited.price
        if edited.product_code: receipt.product_code = edited.product_code
        if edited.in_nsk: receipt.in_nsk = edited.in_nsk
        if edited.add_container: receipt.add_container = edited.add_container
        if edited.comment: receipt.comment = edited.comment
        if edited.carriage_number: receipt.carriage_number = edited.carriage_number
        if edited.status: receipt.status = edited.status
        if edited.date_of_load: receipt.date_of_load = edited.date_of_load

        if edited.city:
            receipt.city_r = await get_if_exist(
                CityORM(name=edited.city, is_paid_entry=False),
                CityORM.name,
                async_session=session
            )

        if edited.forwarder_com_name:
            receipt.forwarder_r = await get_if_exist(
                ForwarderORM(com_name=edited.forwarder_com_name),
                ForwarderORM.com_name,
                async_session=session
            )

        if edited.special_options:
            receipt.special_options_r = [
                await get_if_exist(
                    SpecialOptionORM(name=option, ordered=None),
                    SpecialOptionORM.name,
                    async_session=session
                ) for option in edited.special_options
            ]

        await session.commit()
        receipt = await get_receipt(receipt.id)

        return SReceiptUpdateResult(updated=receipt.updated, data=receipt)


@router.get('/{receipt_id}/pdf')
async def get_receipt_pdf(receipt_id: int) -> FileResponse:
    receipt = await get_receipt(receipt_id)
    return FileResponse(
        path=create_receipt_doc(receipt),
        filename=f'Расписка_{receipt.id}_от_{receipt.created}.pdf',
        media_type='multipart/form-data'
    )
