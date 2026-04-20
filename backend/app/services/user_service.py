from typing import Optional
from app.repositories.user_repo import UserRepository
from app.models.user import UserDB, UserFilter


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        return await self.user_repo.get_user_by_email(email)

    async def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        return await self.user_repo.get_user_by_id(user_id)

    async def create_user(self, user_data: dict) -> UserDB:
        return await self.user_repo.create_user(user_data)

    async def filter_users(self, filters: UserFilter) -> dict:
        return await self.user_repo.filter_users(filters)
