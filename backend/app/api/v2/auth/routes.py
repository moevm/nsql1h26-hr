from fastapi import APIRouter, HTTPException, status, Depends
from neo4j import AsyncDriver

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import UserLogin, TokenResponse, UserResponse
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(driver: AsyncDriver = Depends(get_db)) -> UserService:
    user_repo = UserRepository(driver)
    return UserService(user_repo)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
    )
