from fastapi import FastAPI
from .database.base import Base, engine
from .routes import user, wardrobe

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API")

# Include routers
app.include_router(user.router, prefix="/api", tags=["users"])
app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["wardrobe"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Ai Fashion App!"}