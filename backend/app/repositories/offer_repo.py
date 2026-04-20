from neo4j import AsyncDriver
from uuid import UUID
from app.models.offer import (
    OfferCreate,
    OfferResponse,
    OfferFilter,
    OfferFilterResponse
)


class OfferRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def create_offer(self, offer_data: OfferCreate) -> OfferResponse:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (u:User {id: $created_by})
                MATCH (c:Candidate {id: $candidate_id})
                MATCH (v:Vacancy {id: $vacancy_id})
                CREATE (o:Offer {
                    id: randomUUID(),
                    salary: $salary,
                    start_at: $start_at,
                    status: $status,
                    created_at: timestamp()
                })
                CREATE (u)-[:CREATES]->(o)
                CREATE (o)-[:OFFERED]->(c)
                CREATE (o)-[:CLOSES]->(v)
                SET c.status = 'OFFER'
                RETURN o {
                    .*,
                    candidate_id: c.id,
                    vacancy_id: v.id,
                    created_by: u.id
                } AS offer_data
                """,
                created_by=str(offer_data.created_by),
                candidate_id=str(offer_data.candidate_id),
                vacancy_id=str(offer_data.vacancy_id),
                salary=offer_data.salary,
                start_at=offer_data.start_at,
                status=offer_data.status.value,
            )
            record = await result.single()
            return OfferResponse(**record["offer_data"])

    async def get_offer_by_id(self, offer_id: UUID) -> OfferResponse | None:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (u:User)-[:CREATES]->(o:Offer {id: $offer_id})
                OPTIONAL MATCH (o)-[:OFFERED]->(c:Candidate)
                OPTIONAL MATCH (o)-[:CLOSES]->(v:Vacancy)
                RETURN o {
                    .*,
                    candidate_id: c.id,
                    vacancy_id: v.id,
                    created_by: u.id
                } AS offer_data
                """,
                offer_id=str(offer_id),
            )
            record = await result.single()
            if not record:
                return None
            return OfferResponse(**record["offer_data"])

    async def filter_offers(self, filters: OfferFilter) -> OfferFilterResponse:
        async with self.driver.session() as session:

            base_query = """
            MATCH (o:Offer)
            OPTIONAL MATCH (u:User)-[:CREATES]->(o)
            OPTIONAL MATCH (o)-[:OFFERED]->(c:Candidate)
            OPTIONAL MATCH (o)-[:CLOSES]->(v:Vacancy)
            """
            params = {
                "limit": filters.limit,
                "offset": filters.offset,
                "sort_by": filters.sort_by.value,
                "sort_order": filters.sort_order,
            }
            where_clauses = []

            if filters.salary_from is not None:
                where_clauses.append("o.salary >= $salary_from")
                params["salary_from"] = filters.salary_from
            if filters.salary_to is not None:
                where_clauses.append("o.salary <= $salary_to")
                params["salary_to"] = filters.salary_to
            if filters.status:
                where_clauses.append("o.status = $status")
                params["status"] = filters.status.value
            if filters.start_at_from is not None:
                where_clauses.append("o.start_at >= $start_at_from")
                params["start_at_from"] = filters.start_at_from
            if filters.start_at_to is not None:
                where_clauses.append("o.start_at <= $start_at_to")
                params["start_at_to"] = filters.start_at_to
            if filters.created_at_from is not None:
                where_clauses.append("o.created_at >= $created_at_from")
                params["created_at_from"] = filters.created_at_from
            if filters.created_at_to is not None:
                where_clauses.append("o.created_at <= $created_at_to")
                params["created_at_to"] = filters.created_at_to

            if filters.candidate_id:
                where_clauses.append("c.id = $candidate_id")
                params["candidate_id"] = str(filters.candidate_id)
            if filters.candidate_name:
                where_clauses.append(
                    "toLower(c.full_name) CONTAINS toLower($candidate_name)"
                )
                params["candidate_name"] = filters.candidate_name
            if filters.candidate_email:
                where_clauses.append(
                    "toLower(c.email) CONTAINS toLower($candidate_email)"
                )
                params["candidate_email"] = filters.candidate_email
            if filters.candidate_status:
                where_clauses.append("c.status = $candidate_status")
                params["candidate_status"] = filters.candidate_status

            if filters.vacancy_id:
                where_clauses.append("v.id = $vacancy_id")
                params["vacancy_id"] = str(filters.vacancy_id)
            if filters.vacancy_title:
                where_clauses.append(
                    "toLower(v.title) CONTAINS toLower($vacancy_title)"
                )
                params["vacancy_title"] = filters.vacancy_title
            if filters.vacancy_status:
                where_clauses.append("v.status = $vacancy_status")
                params["vacancy_status"] = filters.vacancy_status

            if filters.created_by:
                where_clauses.append("u.id = $created_by")
                params["created_by"] = str(filters.created_by)
            if filters.created_by_name:
                where_clauses.append(
                    "toLower(u.full_name) CONTAINS toLower($created_by_name)"
                )
                params["created_by_name"] = filters.created_by_name

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            order_by = """
            ORDER BY
                CASE WHEN $sort_by = 'salary' THEN o.salary END {sort_order},
                CASE WHEN $sort_by = 'start_at' THEN o.start_at END {sort_order},
                CASE WHEN $sort_by = 'status' THEN o.status END {sort_order},
                CASE WHEN $sort_by = 'created_at' THEN o.created_at END {sort_order},
                CASE WHEN $sort_by = 'candidate_name' THEN c.full_name END {sort_order},
                CASE WHEN $sort_by = 'vacancy_title' THEN v.title END {sort_order}
            """.replace(
                "{sort_order}", filters.sort_order
            )

            full_query = f"""
            {base_query}
            {where_str}
            WITH o, u, c, v
            {order_by}
            WITH count(o) AS total_count, collect(o {{
                .*,
                candidate_id: c.id,
                vacancy_id: v.id,
                created_by: u.id
            }}) AS items
            RETURN total_count, items[$offset..$offset + $limit] AS offer_data
            """

            result = await session.run(full_query, **params)
            record = await result.single()
            if not record:
                return OfferFilterResponse(total=0, items=[])
            items = (
                [OfferResponse(**item) for item in record["offer_data"]]
                if record["offer_data"]
                else []
            )
            return OfferFilterResponse(total=record["total_count"], items=items)
