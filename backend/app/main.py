from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import lifespan
from app.core.config import settings
from app.core.exceptions import AppError

# Импорт роутеров
from app.api.v2.vacancies.routes import router as vacancy_router

app = FastAPI(title="NoSQL CRM Backend", lifespan=lifespan)

# TODO: check for safety
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(
    vacancy_router,
    prefix=f"{settings.api_prefix}/vacancies", tags=["Vacancies"]
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """
    Общий обработчик исключений.
    Унифицирует отправку кодов ошибок.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "path": request.url.path,
        },
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}
