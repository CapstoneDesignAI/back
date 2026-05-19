from fastapi import APIRouter

from app.api.api import api_router as root_api_router

api_router = APIRouter()
api_router.include_router(root_api_router)
