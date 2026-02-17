from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import db
from app.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    yield
    # Shutdown
    db.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "CRM backend is running"}