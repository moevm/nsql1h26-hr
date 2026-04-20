from neo4j import AsyncDriver
from uuid import UUID
from app.models.vacancy import VacancyCreate, VacancyFilter
from datetime import datetime, timezone


class VacancyRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def create_vacancy(self, vacancy_data: VacancyCreate) -> dict:
        async with self.driver.session() as session:
            created_at = vacancy_data.created_at
            if created_at is None:
                created_at = datetime.now(timezone.utc)
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
                created_at=created_at,
            )
            record = await result.single()
            return record["vacancy_data"] if record else None

    async def get_vacancy_by_id(self, vacancy_id: UUID) -> dict:
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

    async def patch_vacancy(self, vacancy_id: UUID, data: dict) -> dict:
        async with self.driver.session() as session:
            new_status = data.pop("status", None)
            query = "MATCH (v:Vacancy {id: $id}) SET v += $props "
            if new_status:
                query += f" REMOVE v:OPEN, v:CLOSED SET v:{new_status} "
            query += """
                 RETURN v {
            .*,
            status: [label IN labels(v) WHERE label IN ['OPEN', 'CLOSED']][0]
                } AS vacancy_data
                """
            result = await session.run(
                query, id=str(vacancy_id), props=data
                )
            record = await result.single()
            return record["vacancy_data"] if record else None


    async def filter_vacancies(self, filters: VacancyFilter) -> dict:
        async with self.driver.session() as session:

            # Label fitration set
            label_filter = f":{filters.status}" if filters.status else ""
            query_base = f"MATCH (v:Vacancy{label_filter})"

            where_clauses = []
            params = {
                "limit": filters.limit,
                "offset": filters.offset
            }

            if filters.title:
                where_clauses.append("toLower(v.title) CONTAINS toLower($title)")
                params["title"] = filters.title

            if filters.description_contains:
                where_clauses.append("toLower(v.description) CONTAINS toLower($desc)")
                params["desc"] = filters.description_contains

            date_map = {
                "created_at_from": ("v.created_at >= $c_from", "c_from"),
                "created_at_to": ("v.created_at <= $c_to", "c_to"),
                "closed_at_from": ("v.closed_at >= $cl_from", "cl_from"),
                "closed_at_to": ("v.closed_at <= $cl_to", "cl_to")
            }
            for key, (clause, param_name) in date_map.items():
                value = getattr(filters, key, None)
                if value is not None:
                    where_clauses.append(clause)
                    params[param_name] = value

            if filters.has_test_task is not None:
                exists_condition = "" if filters.has_test_task else "NOT"
                where_clauses.append(f"{exists_condition} EXISTS {{ (:TestTask)-[:TEST_FOR]->(v) }}")

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            sort_by = filters.sort_by
            sort_order = filters.sort_order
            # TODO: modify query as in TEST TASK REPO
            full_query = f"""
            {query_base}
            {where_str}
            WITH count(v) AS total_count
            {query_base}
            {where_str}
            RETURN total_count, v {{
                .*,
                status: [label IN labels(v) WHERE label IN ['OPEN', 'CLOSED']][0]
            }} AS vacancy_data
            ORDER BY v.{sort_by} {sort_order}
            SKIP $offset
            LIMIT $limit
            """

            result = await session.run(full_query, **params)
            records = await result.data()

            if not records:
                return {"total": 0, "items": []}

            return {
                "total": records[0]["total_count"],
                "items": [r["vacancy_data"] for r in records]
            }
