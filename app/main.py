from fastapi import FastAPI

from app.router import customer_router


app = FastAPI()
app.include_router(customer_router)
