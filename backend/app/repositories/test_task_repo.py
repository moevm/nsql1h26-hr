from neo4j import AsyncDriver
from uuid import UUID

from app.models.test_task import TestTaskCreate

class TestTaskRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    
    async def create_test_task(self, test_task_data: TestTaskCreate) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (v:Vacancy{id: $vacancy_id})
                CREATE (t:TestTask{
                    id: randomUUID(), 
                    title: $title,
                    test_task_url: $url
                })-[:TEST_FOR]->(v)
                RETURN t { .*, vacancy_id: v.id } AS test_task_data
                """,
                vacancy_id=str(test_task_data.vacancy_id),
                title=test_task_data.title,
                url=str(test_task_data.test_task_url)
            )
            record = await result.single()
            return record["test_task_data"] if record else None