#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Neo4jDB
from app.core.config import settings

from app.models.user import UserCreate
from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository

USERS = [
    UserCreate(
        email="admin@example.com",
        full_name="Администратор",
        password="admin123",
        role="ADMIN",
    ),
    UserCreate(
        email="hr@example.com",
        full_name="HR Менеджер",
        password="hr123",
        role="HR",
    ),
    UserCreate(
        email="manager@example.com",
        full_name="Руководитель",
        password="manager123",
        role="MANAGER",
    ),
    UserCreate(
        email="tech@example.com",
        full_name="Технический специалист",
        password="tech123",
        role="TECH_SPEC",
    ),
]


async def seed():
    await Neo4jDB.connect()
    driver = Neo4jDB.get_driver()

    repo = UserRepository(driver)
    service = UserService(repo)

    for data in USERS:
        existing = await service.get_user_by_email(data.email)
        if existing:
            print(f"{data.email} already exists")
            continue

        user = await service.create_user(data)
        print(f"Created: {user.email} ({user.role})")

    await Neo4jDB.close()


if __name__ == "__main__":
    asyncio.run(seed())
