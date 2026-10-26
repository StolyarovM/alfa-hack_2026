
from fastapi import APIRouter
from app.api.routes import auth, profile, products, applications
api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
