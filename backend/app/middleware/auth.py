from fastapi import Request, HTTPException, status
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
        print(f"[AuthMiddleware] Checking path: {path}")  # отладка

        if any(path.startswith(public_path) for public_path in PUBLIC_PATHS):
            print(f"[AuthMiddleware] Path {path} is public, skipping auth")
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print(f"[AuthMiddleware] Missing or invalid auth header for {path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.replace("Bearer ", "")

        try:
            payload = decode_token(token)
            request.state.user = payload
            print(f"[AuthMiddleware] User authenticated: {payload.get('email')}")
        except Exception as e:
            print(f"[AuthMiddleware] Token decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

        return await call_next(request)
