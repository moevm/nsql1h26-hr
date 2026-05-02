from fastapi import APIRouter, Depends, status
from neo4j import AsyncDriver
from typing import Annotated
from uuid import UUID

from app.core.database import get_db
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository
from app.models.user import UserFilter, UserFilterResponse, UserResponse
from app.core.security import require_role

router = APIRouter()


def get_user_service(driver: AsyncDriver = Depends(get_db)) -> UserService:
    user_repo = UserRepository(driver)
    return UserService(user_repo)


@router.get("", response_model=UserFilterResponse)
async def filter_users(
    filters: Annotated[UserFilter, Depends()],
    user_service: UserService = Depends(get_user_service),
    ##current_user: dict = Depends(require_role('ADMIN')),
):
    result = await user_service.filter_users(filters)
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    ##current_user: dict = Depends(require_role('ADMIN')),
):
    user = await user_service.get_user_by_id(str(user_id))
    if not user:
        from app.core.exceptions import AppError

        raise AppError("User not found", status.HTTP_404_NOT_FOUND)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(require_role("ADMIN")),
):
    if str(user_id) == current_user.get("id"):
        from app.core.exceptions import AppError

        raise AppError("Cannot delete your own account", status.HTTP_400_BAD_REQUEST)

    deleted = await user_service.delete_user(str(user_id))
    if not deleted:
        from app.core.exceptions import AppError

        raise AppError("User not found", status.HTTP_404_NOT_FOUND)
    return None
