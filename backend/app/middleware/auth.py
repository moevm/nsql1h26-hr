from fastapi import Request, status
from fastapi.responses import JSONResponse # Добавьте этот импорт
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token

PUBLIC_PATHS = [
    "/health",
    "/api/v2/auth/login",
    "/api/v2/auth/register",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path

        if any(path.startswith(public_path) for public_path in PUBLIC_PATHS):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Вместо raise используем return JSONResponse
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.replace("Bearer ", "")

        try:
            payload = decode_token(token)
            request.state.user = payload
        except Exception as e:
            # Здесь также возвращаем JSONResponse
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
