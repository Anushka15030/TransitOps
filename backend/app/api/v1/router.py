# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1 import auth

api_router = APIRouter()
api_router.include_router(auth.router)
# Future modules append here: api_router.include_router(vehicles.router)

# app/api/v1/router.py
from app.api.v1 import auth, vehicles

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(vehicles.router)