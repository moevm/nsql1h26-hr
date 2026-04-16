from neo4j import AsyncDriver
from uuid import UUID
from app.models.vacancy import VacancyCreate


class VacancyRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def create_vacancy(self, vacancy_data: VacancyCreate) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                f"""
                CREATE (v:Vacancy:{vacancy_data.status} {{
                    id: randomUUID(),
                    title: $title,
                    description: $description,
                    created_at: $created_at
                }})
                RETURN v {{
            .*,
            status: [label IN labels(v) WHERE label IN ['OPEN', 'CLOSED']][0]
                }} AS vacancy_data
                """,
                title=vacancy_data.title,
                description=vacancy_data.description,
                created_at=vacancy_data.created_at,
            )
            record = await result.single()
            return record["vacancy_data"] if record else None

    async def get_vacancy_by_id(self, vacancy_id: UUID):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (v:Vacancy {id: $id})
                RETURN v {
            .*,
            status: [label IN labels(v) WHERE label IN ['OPEN', 'CLOSED']][0]
                } AS vacancy_data
                """,
                id=str(vacancy_id)
                )
            record = await result.single()
            return record["vacancy_data"] if record else None
