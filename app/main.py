from fastapi import FastAPI

from app.routers import receipts_router, crate_router, part_ship_router


app = FastAPI()

app.include_router(receipts_router)
app.include_router(crate_router)
app.include_router(part_ship_router)
