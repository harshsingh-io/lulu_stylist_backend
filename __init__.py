from fastapi import FastAPI
from appp.routes import user as user_routes

def create_app() -> FastAPI:
    app = FastAPI(title="User API", version="1.0.0")
    app.include_router(user_routes.router, prefix="/api/v1")
    return app