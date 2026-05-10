from typing import Optional, List
from app.core.security import get_password_hash
from app.repositories.user_repo import UserRepository
from app.models.user import UserDB, UserFilter, UserCreate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        return await self.user_repo.get_user_by_email(email)

    async def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        return await self.user_repo.get_user_by_id(user_id)

    async def get_users(self) -> List[UserDB]:
        return await self.user_repo.get_users()

    async def create_user(self, user_data: UserCreate) -> UserDB:
        user_data_raw = user_data.model_dump()
        hashed = get_password_hash(user_data.password)
        user_data_raw["password_hash"] = hashed
        user_data_raw.pop("password")
        return await self.user_repo.create_user(user_data_raw)

    async def filter_users(self, filters: UserFilter) -> dict:
        return await self.user_repo.filter_users(filters)
