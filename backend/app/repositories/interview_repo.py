from neo4j import AsyncDriver
from uuid import UUID
from app.models.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewFilter,
    InterviewFilterResponse,
    InterviewPatch,
)


class InterviewRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def create_interview(
        self, interview_data: InterviewCreate
    ) -> InterviewResponse:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Candidate {id: $candidate_id})
                MATCH (u:User:TECH_SPEC {id: $tech_spec_id})
                CREATE (i:Interview {
                    id: randomUUID(),
                    scheduled_at: $scheduled_at,
                    zoom_url: $zoom_url,
                    feedback: $feedback,
                    result: $result
                })
                CREATE (c)-[:ASSIGNED_FOR]->(i)
                CREATE (u)-[:INTERVIEWING]->(i)
                RETURN i {
                    .*,
                    candidate_id: c.id,
                    tech_spec_id: u.id
                } AS interview_data
                """,
                candidate_id=str(interview_data.candidate_id),
                tech_spec_id=str(interview_data.tech_spec_id),
                scheduled_at=interview_data.scheduled_at,
                zoom_url=(
                    str(interview_data.zoom_url) if interview_data.zoom_url else None
                ),
                feedback=interview_data.feedback,
                result=(
                    interview_data.result.value
                    if interview_data.result
                    else "AWAIT_INTERVIEW"
                ),
            )
            record = await result.single()
            if not record:
                return None
            return InterviewResponse(**record["interview_data"])

    async def patch_interview(
        self, interview_id: UUID, patch: dict
    ) -> InterviewResponse:
        async with self.driver.session() as session:
            query = """
            MATCH (i:Interview {id: $id})
            MATCH (c:Candidate)-[:ASSIGNED_FOR]->(i)
            MATCH (u:User:TECH_SPEC)-[:INTERVIEWING]->(i)
            SET i += $props
            RETURN i {
                .*,
                candidate_id: c.id,
                tech_spec_id: u.id
            } AS interview_data
            """
            result = await session.run(query, id=str(interview_id), props=patch)
            record = await result.single()
            if not record:
                return None
            return InterviewResponse(**record["interview_data"])

    async def get_interview_by_id(self, interview_id: UUID) -> InterviewResponse | None:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Candidate)-[:ASSIGNED_FOR]->(i:Interview {id: $interview_id})<-[:INTERVIEWING]-(u:User:TECH_SPEC)
                RETURN i {
                    .*,
                    candidate_id: c.id,
                    tech_spec_id: u.id
                } AS interview_data
                """,
                interview_id=str(interview_id),
            )
            record = await result.single()
            if not record:
                return None
            return InterviewResponse(**record["interview_data"])

    async def filter_interviews(
        self, filters: InterviewFilter
    ) -> InterviewFilterResponse:
        async with self.driver.session() as session:
            params = {
                "limit": filters.limit,
                "offset": filters.offset,
            }
            where_clauses = []

            if filters.candidate_id:
                where_clauses.append(
                    "EXISTS { (c:Candidate {id: $candidate_id})-[:ASSIGNED_FOR]->(i) }"
                )
                params["candidate_id"] = str(filters.candidate_id)

            if filters.candidate_name:
                where_clauses.append(
                    "EXISTS { (c:Candidate)-[:ASSIGNED_FOR]->(i) WHERE toLower(c.full_name) CONTAINS toLower($candidate_name) }"
                )
                params["candidate_name"] = filters.candidate_name

            if filters.tech_spec_id:
                where_clauses.append(
                    "EXISTS { (u:User:TECH_SPEC {id: $tech_spec_id})-[:INTERVIEWING]->(i) }"
                )
                params["tech_spec_id"] = str(filters.tech_spec_id)

            if filters.tech_spec_name:
                where_clauses.append(
                    "EXISTS { (u:User:TECH_SPEC)-[:INTERVIEWING]->(i) WHERE toLower(u.full_name) CONTAINS toLower($tech_spec_name) }"
                )
                params["tech_spec_name"] = filters.tech_spec_name

            if filters.result:
                where_clauses.append("i.result = $result")
                params["result"] = filters.result.value

            if filters.feedback_contains:
                where_clauses.append(
                    "toLower(i.feedback) CONTAINS toLower($feedback_contains)"
                )
                params["feedback_contains"] = filters.feedback_contains

            if filters.scheduled_at_from is not None:
                where_clauses.append("i.scheduled_at >= $scheduled_at_from")
                params["scheduled_at_from"] = filters.scheduled_at_from

            if filters.scheduled_at_to is not None:
                where_clauses.append("i.scheduled_at <= $scheduled_at_to")
                params["scheduled_at_to"] = filters.scheduled_at_to

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            universal_query = f"""
            MATCH (i:Interview)
            MATCH (c:Candidate)-[:ASSIGNED_FOR]->(i)
            MATCH (u:User:TECH_SPEC)-[:INTERVIEWING]->(i)
            {where_str}
            WITH i, c, u
            ORDER BY
                CASE WHEN $sort_by = 'scheduled_at' THEN i.scheduled_at END {filters.sort_order},
                CASE WHEN $sort_by = 'result' THEN i.result END {filters.sort_order},
                CASE WHEN $sort_by = 'candidate_name' THEN c.full_name END {filters.sort_order},
                CASE WHEN $sort_by = 'tech_spec_name' THEN u.full_name END {filters.sort_order}
            WITH count(i) AS total_count, collect(i {{
                .*,
                candidate_id: c.id,
                tech_spec_id: u.id
            }}) AS items
            RETURN total_count, items[$offset..$offset + $limit] AS interview_data
            """
            params["sort_by"] = filters.sort_by.value
            result = await session.run(universal_query, **params)
            record = await result.single()
            if not record:
                return InterviewFilterResponse(total=0, items=[])
            items = (
                [InterviewResponse(**item) for item in record["interview_data"]]
                if record["interview_data"]
                else []
            )
            return InterviewFilterResponse(total=record["total_count"], items=items)

    async def restore_interview(
        self, interview: InterviewResponse
    ) -> InterviewResponse:
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Candidate {id: $candidate_id})
                MATCH (u:User:TECH_SPEC {id: $tech_spec_id})
                CREATE (i:Interview {
                    id: $id,
                    scheduled_at: $scheduled_at,
                    zoom_url: $zoom_url,
                    feedback: $feedback,
                    result: $result
                })
                CREATE (c)-[:ASSIGNED_FOR]->(i)
                CREATE (u)-[:INTERVIEWING]->(i)
                RETURN i {
                    .*,
                    candidate_id: c.id,
                    tech_spec_id: u.id
                } AS interview_data
                """,
                id=str(interview.id),
                candidate_id=str(interview.candidate_id),
                tech_spec_id=str(interview.tech_spec_id),
                scheduled_at=interview.scheduled_at,
                zoom_url=(
                    str(interview.zoom_url) if interview.zoom_url else None
                ),
                feedback=interview.feedback,
                result=(
                    interview.result.value
                    if interview.result
                    else "AWAIT_INTERVIEW"
                ),
            )
            record = await result.single()
            if not record:
                return None
            return InterviewResponse(**record["interview_data"])
