import pytest
import uuid
from neo4j import AsyncGraphDatabase
from testcontainers.neo4j import Neo4jContainer
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token


@pytest.fixture(scope="session")
def neo4j_container():
    """Запускает Neo4j в Docker на время сессии тестов."""
    with Neo4jContainer("neo4j:5") as container:
        # Можно настроить дополнительные параметры
        container.with_env("NEO4J_PLUGINS", '["apoc"]')
        yield container


@pytest.fixture
async def neo4j_driver(neo4j_container):
    """Создаёт асинхронный драйвер для тестовой БД."""
    uri = neo4j_container.get_connection_url()
    auth = ("neo4j", "password")

    driver = AsyncGraphDatabase.driver(uri, auth=auth)
    await driver.verify_connectivity()
    yield driver
    await driver.close()


@pytest.fixture(autouse=True)
async def clean_graph(neo4j_driver):
    """Очищает все узлы и связи перед каждым тестом."""
    async with neo4j_driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    yield


# Dependency overrides для FastAPI
@pytest.fixture(autouse=True)
def override_dependencies(neo4j_driver):
    """Подменяет зависимость get_db на тестовый драйвер."""

    async def _get_test_db():
        return neo4j_driver

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


# HTTP клиент для API тестов
@pytest.fixture
async def async_client():
    """Асинхронный клиент для тестирования эндпоинтов."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/api/v2"
    ) as client:
        yield client


@pytest.fixture
async def auth_client(async_client, neo4j_driver):
    """Клиент с предустановленным токеном авторизации."""
    user_id = str(uuid.uuid4())
    token_data = {"sub": user_id, "email": "default@example.com", "role": "default"}

    token = create_access_token(token_data)
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client


# Клиенты с конкретными ролями


@pytest.fixture
async def admin_client(async_client, neo4j_driver):
    """Клиент с предустановленным токеном авторизации."""
    user_id = str(uuid.uuid4())
    token_data = {"sub": user_id, "email": "admin@example.com", "role": "ADMIN"}

    token = create_access_token(token_data)
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client


@pytest.fixture
async def hr_client(async_client, neo4j_driver):
    """Клиент с предустановленным токеном авторизации."""
    user_id = str(uuid.uuid4())
    token_data = {"sub": user_id, "email": "hr@example.com", "role": "HR"}

    token = create_access_token(token_data)
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client


@pytest.fixture
async def manager_client(async_client, neo4j_driver):
    """Клиент с предустановленным токеном авторизации."""
    user_id = str(uuid.uuid4())
    token_data = {"sub": user_id, "email": "manager@example.com", "role": "MANAGER"}

    token = create_access_token(token_data)
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client


@pytest.fixture
async def tech_spec_client(async_client, neo4j_driver):
    """Клиент с предустановленным токеном авторизации."""
    user_id = str(uuid.uuid4())
    token_data = {"sub": user_id, "email": "tech_spec@example.com", "role": "TECH_SPEC"}

    token = create_access_token(token_data)
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client
