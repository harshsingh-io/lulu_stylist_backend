from fastapi import FastAPI
from .database.base import Base, engine
from .routes import user, wardrobe, upload, chat
from .database.mongodb import MongoDB
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ai Fashion App", version="0.1")


@app.on_event("startup")
async def startup_db_client():
    await MongoDB.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await MongoDB.close_mongo_connection()

# Include routers
app.include_router(user.router, prefix="/api", tags=["users"])
app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["wardrobe"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(upload.router, prefix="/api", tags=["uploads"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Ai Fashion App!"}