from neo4j import AsyncDriver
from uuid import UUID

from app.models.test_task import (
    TestTaskCreate,
    TestTasksFilter,
    TestTaskSort,
    TestTaskResponse,
)


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
                url=str(test_task_data.test_task_url),
            )
            record = await result.single()
            return record["test_task_data"] if record else None

    async def get_test_task_by_id(self, test_task_id: dict) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (t:TestTask{id: $test_task_id})-[:TEST_FOR]->(v:Vacancy)
                RETURN t { .*, vacancy_id: v.id } AS test_task_data
                """,
                test_task_id=str(test_task_id),
            )
            record = await result.single()
            return record["test_task_data"] if record else None

    async def patch_test_task(
        self, test_task_id: UUID, test_task_data: TestTaskCreate
    ) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (t:TestTask{id: $test_task_id})-[:TEST_FOR]->(v:Vacancy) SET t += $props
                RETURN t { .*, vacancy_id: v.id } AS test_task_data
                """,
                test_task_id=str(test_task_id),
                props=test_task_data,
            )
            record = await result.single()
            return record["test_task_data"] if record else None

    async def filter_test_tasks(self, filters: TestTasksFilter) -> dict:
        async with self.driver.session() as session:
            match_base = "MATCH (t:TestTask)-[:TEST_FOR]->"
            params = {"limit": filters.limit, "offset": filters.offset}
            if filters.vacancy_id:
                match_base += "(v:Vacancy{id:$vacancy_id})"
                params["vacancy_id"] = str(filters.vacancy_id)
            else:
                match_base += "(v:Vacancy)"
            where_clauses = []
            if filters.has_assigned_candidates is not None:
                exists_condition = "" if filters.has_assigned_candidates else "NOT"
                where_clauses.append(
                    f"{exists_condition} EXISTS {{ (:Candidate)-[:COMPLETES]->(t) }}"
                )
            if filters.vacancy_title:
                where_clauses.append(
                    "toLower(v.title) CONTAINS toLower($vacancy_title)"
                )
                params["vacancy_title"] = filters.vacancy_title
            if filters.title:
                where_clauses.append("toLower(t.title) CONTAINS toLower($title)")
                params["title"] = filters.title
            if filters.test_task_url_contains:
                where_clauses.append(
                    "toLower(t.test_task_url) CONTAINS toLower($test_task_url)"
                )
                params["test_task_url"] = filters.test_task_url_contains

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            if filters.sort_by == TestTaskSort.VACANCY_ID:
                order_by_clause = f"v.id {filters.sort_order}"
            else:
                order_by_clause = f"t.{filters.sort_by} {filters.sort_order}"
            full_query = f"""
            {match_base}
            {where_str}
            WITH t, v
            ORDER BY {order_by_clause}
            WITH count(t) AS total_count, collect(t {{ .*, vacancy_id: v.id }}) AS items
            RETURN total_count, items[$offset..$offset + $limit] AS test_task_data
            """

            result = await session.run(full_query, **params)
            record = await result.single()

            if not record:
                return {"total": 0, "items": []}

            return {"total": record["total_count"], "items": record["test_task_data"]}

    async def restore_test_task(self, test_task: TestTaskResponse) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (v:Vacancy{id: $vacancy_id})
                CREATE (t:TestTask{
                    id: $id,
                    title: $title,
                    test_task_url: $url
                })-[:TEST_FOR]->(v)
                RETURN t { .*, vacancy_id: v.id } AS test_task_data
                """,
                id=str(test_task.id),
                vacancy_id=str(test_task.vacancy_id),
                title=test_task.title,
                url=str(test_task.test_task_url),
            )
            record = await result.single()
            return record["test_task_data"] if record else None
