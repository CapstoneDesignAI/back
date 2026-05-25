from fastapi import APIRouter

from app.api.v1.auth.kakao import router as auth_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.routes import router as routes_router
from app.api.v1.endpoints.recommendations import router as recommendations_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(user_router, tags=["user"])
api_router.include_router(routes_router, tags=["routes"])
api_router.include_router(recommendations_router, tags=["ai-recommendations"])