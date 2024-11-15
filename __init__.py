# app/__init__.py
from fastapi import FastAPI
from app.routes import user, auth
from app.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="User API",
        version="1.0.0",
        description="User API with JWT Authentication"
    )
    
    # Include routers
    app.include_router(
        auth.router,
        prefix=settings.API_V1_STR,
        tags=["authentication"]
    )
    app.include_router(
        user.router,
        prefix=settings.API_V1_STR,
        tags=["users"]
    )
    
    return app