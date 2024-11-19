from fastapi import FastAPI
from .database.base import Base, engine
from .routes import user, wardrobe, upload

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ai Fashion App", version="0.1")

# Include routers
app.include_router(user.router, prefix="/api", tags=["users"])
app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["wardrobe"])

app.include_router(upload.router, prefix="/api", tags=["uploads"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Ai Fashion App!"}