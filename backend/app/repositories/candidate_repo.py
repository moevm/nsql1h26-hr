from neo4j import AsyncDriver
from uuid import UUID
from app.models.candidate import CandidateCreate


class CandidateRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def create_candidate(self, candidate_data: CandidateCreate) -> dict:
        async with self.driver.session() as session:
            resume_url_str = (
                ", resume_url: $resume_url" if candidate_data.resume_url else ""
            )
            create_query = f"""
                CREATE (c:Candidate:{candidate_data.status}{{
                    id: randomUUID(),
                    full_name: $full_name,
                    email: $email,
                    phone: $phone
                    {resume_url_str}
                }})
                """
            params = {
                "full_name": candidate_data.full_name,
                "email": candidate_data.email,
                "phone": candidate_data.phone,
            }
            if candidate_data.vacancy_id:
                params["vacancy_id"] = str(candidate_data.vacancy_id)
                create_query = (
                    " MATCH (v:Vacancy{id: $vacancy_id}) "
                    + create_query
                    + " CREATE (c)-[:APPLIES]->(v) "
                )
            if candidate_data.test_task_id:
                params["test_task_id"] = str(candidate_data.test_task_id)
                create_query = (
                    "MATCH (t:TestTask{id: $test_task_id})"
                    + create_query
                    + " CREATE (c)-[:COMPLETES]->(t) "
                )
            if candidate_data.resume_url:
                params["resume_url"] = str(candidate_data.resume_url)
            vacancy_str = (
                ", vacancy_id: $vacancy_id" if candidate_data.vacancy_id else ""
            )
            test_task_id_str = (
                ", test_task_id: $test_task_id" if candidate_data.test_task_id else ""
            )
            create_query += f"""
            RETURN c {{
                .*
                {vacancy_str}
                {test_task_id_str},
                status: [label IN labels(c) WHERE label in ['NEW', 'TEST', 'INTERVIEW', 'OFFER', 'REJECTED', 'HIRED']][0]
            }}  AS candidate_data
            """
            result = await session.run(create_query, **params)
            record = await result.single()
            return record["candidate_data"] if record else None

    async def get_candidate_by_id(self, candidate_id: UUID) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Candidate{id:$candidate_id})
                OPTIONAL MATCH (c)-[:APPLIES]->(v:Vacancy)
                OPTIONAL MATCH (c)-[:COMPLETES]->(t:TestTask)
                RETURN c {
                    .*,
                    vacancy_id: v.id,
                    test_task_id: t.id,
                    status: [label IN labels(c) WHERE label in ['NEW', 'TEST', 'INTERVIEW', 'OFFER', 'REJECTED', 'HIRED']][0]
                } AS candidate_data
                """,
                candidate_id=str(candidate_id)
            )
            record = await result.single()
            if not record:
                return None
            data = record["candidate_data"]
            return {k: v for k, v in data.items() if v is not None}
