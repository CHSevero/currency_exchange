from fastapi import APIRouter

from app.api.endpoints import converter, transactions

api_router = APIRouter()

# Include all endpoint routers with prefixes
api_router.include_router(converter.router, prefix="/convert", tags=["currency"])

api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
