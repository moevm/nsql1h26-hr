from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from neo4j import AsyncDriver, AsyncGraphDatabase

from config import settings


class Neo4jDB:
    driver: Optional[AsyncDriver] = None

    @classmethod
    async def connect(cls) -> None:
        cls.driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        await cls.driver.verify_connectivity()

    @classmethod
    async def close(cls) -> None:
        if cls.driver:
            await cls.driver.close()
            cls.driver = None

    @classmethod
    def get_driver(cls) -> AsyncDriver:
        if cls.driver is None:
            raise RuntimeError("Neo4j driver not initialized")
        return cls.driver


# Lifespan менеджер для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await Neo4jDB.connect()
    yield
    await Neo4jDB.close()


# Зависимость для получения драйвера
async def get_db() -> AsyncDriver:
    return Neo4jDB.get_driver()
