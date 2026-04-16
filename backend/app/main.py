from fastapi import FastAPI
from core.database import lifespan
from core.config import settings

# TODO: импортировать роутеры позже
# from app.api.v1.users.routes import router as users_router
# from app.api.v1.orders.routes import router as orders_router

app = FastAPI(
    title="NoSQL CRM Backend",
    lifespan=lifespan
)

# TODO: Подключение роутеров
# app.include_router(users_router, prefix=f"{settings.api_v1_prefix}/users", tags=["users"])
# app.include_router(orders_router, prefix=f"{settings.api_v1_prefix}/orders", tags=["orders"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
