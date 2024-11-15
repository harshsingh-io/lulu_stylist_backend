from fastapi import FastAPI
from .database.base import Base, engine
from .routes import user

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API")

# Include routers
app.include_router(user.router, prefix="/api", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to User Management API"}