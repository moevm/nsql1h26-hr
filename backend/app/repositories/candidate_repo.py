from neo4j import AsyncDriver
from uuid import UUID
from app.models.candidate import (
    CandidateStatus,
    CandidateCreate,
    CandidateSort,
    CandidateFilter,
)


class CandidateRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver
        self.statuses = ", ".join(f"'{c}'" for c in CandidateStatus)

    async def create_candidate(self, candidate_data: CandidateCreate) -> dict:
        async with self.driver.session() as session:
            params = {
                "full_name": candidate_data.full_name,
                "email": candidate_data.email,
                "phone": candidate_data.phone,
            }

            create_query = f"""
                CREATE (c:Candidate:{candidate_data.status} {{
                    id: randomUUID(),
                    full_name: $full_name,
                    email: $email,
                    phone: $phone
            """

            if candidate_data.resume_url:
                params["resume_url"] = str(candidate_data.resume_url)
                create_query += ", resume_url: $resume_url"

            create_query += "})"

            if candidate_data.vacancy_id:
                params["vacancy_id"] = str(candidate_data.vacancy_id)
                create_query = (
                    "MATCH (v:Vacancy {id: $vacancy_id}) "
                    + create_query
                    + " CREATE (c)-[:APPLIES]->(v) "
                )

            if candidate_data.test_task_id:
                params["test_task_id"] = str(candidate_data.test_task_id)
                create_query = (
                    "MATCH (t:TestTask {id: $test_task_id}) "
                    + create_query
                    + " CREATE (c)-[:COMPLETES]->(t) "
                )

            create_query += " RETURN c.id as id"

            result = await session.run(create_query, **params)
            record = await result.single()
            if not record:
                return None

            candidate_id = record["id"]

            get_query = f"""
                MATCH (c:Candidate {{id: $candidate_id}})
                OPTIONAL MATCH (c)-[:APPLIES]->(v:Vacancy)
                OPTIONAL MATCH (c)-[:COMPLETES]->(t:TestTask)
                RETURN c {{
                    .*,
                    vacancy_id: v.id,
                    test_task_id: t.id,
                    status: [label IN labels(c) WHERE label in [{self.statuses}]][0]
                }} AS candidate_data
            """
            result = await session.run(get_query, candidate_id=candidate_id)
            record = await result.single()
            if record:
                data = dict(record["candidate_data"])
                return {k: v for k, v in data.items() if v is not None}
            return None

    async def get_candidate_by_id(self, candidate_id: UUID) -> dict:
        async with self.driver.session() as session:
            result = await session.run(
                f"""
                MATCH (c:Candidate {{id: $candidate_id}})
                OPTIONAL MATCH (c)-[:APPLIES]->(v:Vacancy)
                OPTIONAL MATCH (c)-[:COMPLETES]->(t:TestTask)
                RETURN c {{
                    .*,
                    vacancy_id: v.id,
                    test_task_id: t.id,
                    status: [label IN labels(c) WHERE label in [{self.statuses}]][0]
                }} AS candidate_data
                """,
                candidate_id=str(candidate_id),
            )
            record = await result.single()
            if not record:
                return None
            data = record["candidate_data"]
            return {k: v for k, v in data.items() if v is not None}

    async def patch_candidate(self, candidate_id: UUID, candidate_data: dict) -> dict:
        async with self.driver.session() as session:
            new_status = candidate_data.pop("status", None)
            vacancy_id = candidate_data.pop("vacancy_id", None)
            test_task_id = candidate_data.pop("test_task_id", None)

            tx = await session.begin_transaction()
            try:
                if candidate_data:
                    await tx.run(
                        "MATCH (c:Candidate {id: $id}) SET c += $props",
                        id=str(candidate_id),
                        props=candidate_data,
                    )
                if new_status:
                    remove_labels = " REMOVE " + ", ".join(
                        f"c:{s}" for s in CandidateStatus
                    )
                    set_label = f" SET c:{new_status}"
                    await tx.run(
                        f"MATCH (c:Candidate {{id: $id}}){remove_labels}{set_label}",
                        id=str(candidate_id),
                    )

                if vacancy_id is not None:
                    await tx.run(
                        "MATCH (c:Candidate {id: $id})-[r:APPLIES]->() DELETE r",
                        id=str(candidate_id),
                    )
                    if vacancy_id:
                        await tx.run(
                            "MATCH (c:Candidate {id: $id}), (v:Vacancy {id: $vid}) "
                            "CREATE (c)-[:APPLIES]->(v)",
                            id=str(candidate_id),
                            vid=str(vacancy_id),
                        )

                if test_task_id is not None:
                    await tx.run(
                        "MATCH (c:Candidate {id: $id})-[r:COMPLETES]->() DELETE r",
                        id=str(candidate_id),
                    )
                    if test_task_id:
                        await tx.run(
                            "MATCH (c:Candidate {id: $id}), (t:TestTask {id: $tid}) "
                            "CREATE (c)-[:COMPLETES]->(t)",
                            id=str(candidate_id),
                            tid=str(test_task_id),
                        )

                await tx.commit()
            except Exception:
                await tx.rollback()
                raise

            result = await session.run(
                f"""
                MATCH (c:Candidate {{id: $candidate_id}})
                OPTIONAL MATCH (c)-[:APPLIES]->(v:Vacancy)
                OPTIONAL MATCH (c)-[:COMPLETES]->(t:TestTask)
                RETURN c {{
                    .*,
                    vacancy_id: v.id,
                    test_task_id: t.id,
                    status: [label IN labels(c) WHERE label IN [{self.statuses}]][0]
                }} AS candidate_data
                """,
                candidate_id=str(candidate_id),
            )
            record = await result.single()
            if not record:
                return None
            data = record["candidate_data"]
            return {k: v for k, v in data.items() if v is not None}

    async def filter_candidates(self, filters: CandidateFilter) -> dict:
        async with self.driver.session() as session:
            label_filter = f":{filters.status}" if filters.status else ""
            match_base = f"MATCH (c:Candidate{label_filter})"
            params = {"limit": filters.limit, "offset": filters.offset}
            where_clauses = []

            if filters.full_name:
                where_clauses.append(
                    "toLower(c.full_name) CONTAINS toLower($full_name)"
                )
                params["full_name"] = filters.full_name
            if filters.email:
                where_clauses.append("toLower(c.email) CONTAINS toLower($email)")
                params["email"] = filters.email
            if filters.phone:
                where_clauses.append("toLower(c.phone) CONTAINS toLower($phone)")
                params["phone"] = filters.phone
            if filters.resume_url_contains:
                where_clauses.append(
                    "toLower(c.resume_url) CONTAINS toLower($resume_url_contains)"
                )
                params["resume_url_contains"] = str(filters.resume_url_contains)

            if filters.vacancy_id:
                where_clauses.append(
                    "EXISTS { (c)-[:APPLIES]->(v:Vacancy {id: $vacancy_id}) }"
                )
                params["vacancy_id"] = str(filters.vacancy_id)
            if filters.vacancy_title:
                where_clauses.append(
                    "EXISTS { (c)-[:APPLIES]->(v:Vacancy) WHERE toLower(v.title) CONTAINS toLower($vacancy_title) }"
                )
                params["vacancy_title"] = filters.vacancy_title

            if filters.test_task_id:
                where_clauses.append(
                    "EXISTS { (c)-[:COMPLETES]->(t:TestTask {id: $test_task_id}) }"
                )
                params["test_task_id"] = str(filters.test_task_id)
            if filters.test_task_title:
                where_clauses.append(
                    "EXISTS { (c)-[:COMPLETES]->(t:TestTask) WHERE toLower(t.title) CONTAINS toLower($test_task_title) }"
                )
                params["test_task_title"] = filters.test_task_title

            if filters.has_interview is not None:
                exists_condition = "" if filters.has_interview else "NOT"
                where_clauses.append(
                    f"{exists_condition} EXISTS {{ (c)-[:ASSIGNED_FOR]->(:Interview) }}"
                )

            if filters.has_offer is not None:
                exists_condition = "" if filters.has_offer else "NOT"
                where_clauses.append(
                    f"{exists_condition} EXISTS {{ (:Offer)-[:OFFERED]->(c) }}"
                )

            where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

            sort_mapping = {
                CandidateSort.FULL_NAME: "c.full_name",
                CandidateSort.EMAIL: "c.email",
                CandidateSort.STATUS: "status",
                CandidateSort.CREATED_AT: "c.created_at",
            }
            sort_field = sort_mapping.get(filters.sort_by, "c.created_at")
            order_by_clause = f"{sort_field} {filters.sort_order.value}"

            full_query = f"""
                {match_base}
                {where_str}
                OPTIONAL MATCH (c)-[:APPLIES]->(v:Vacancy)
                OPTIONAL MATCH (c)-[:COMPLETES]->(t:TestTask)
                WITH c, v.id as vacancy_id, t.id as test_task_id, [label IN labels(c) WHERE label IN [{self.statuses}]][0] AS status
                ORDER BY {order_by_clause}
                WITH count(c) AS total_count, collect(c {{
                    .*,
                    vacancy_id: vacancy_id,
                    test_task_id: test_task_id,
                    status: [label IN labels(c) WHERE label in [{self.statuses}]][0]
                }}) AS items
                RETURN total_count, items[$offset..$offset + $limit] AS candidate_data
            """

            result = await session.run(full_query, **params)
            record = await result.single()

            if not record:
                return {"total": 0, "items": []}

            items = (
                [dict(node) for node in record["candidate_data"]]
                if record["candidate_data"]
                else []
            )
            return {"total": record["total_count"], "items": items}
