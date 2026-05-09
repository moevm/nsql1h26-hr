from neo4j import AsyncDriver
from uuid import uuid4
from typing import Optional
from app.models.user import UserDB, UserFilter, UserCreate


class UserRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        query = """
        MATCH (u:User {email: $email})
        RETURN u.id as id, u.email as email, u.full_name as full_name,
               u.password_hash as password_hash, u.role as role
        """
        result = await self.driver.execute_query(query, email=str(email))
        if result.records:
            record = result.records[0]
            return UserDB(
                id=record["id"],
                email=record["email"],
                full_name=record["full_name"],
                password_hash=record["password_hash"],
                role=record["role"],
            )
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserDB]:
        query = """
        MATCH (u:User {id: $user_id})
        RETURN u.id as id, u.email as email, u.full_name as full_name,
               u.password_hash as password_hash, u.role as role
        """
        result = await self.driver.execute_query(query, user_id=str(user_id))
        if result.records:
            record = result.records[0]
            return UserDB(
                id=record["id"],
                email=record["email"],
                full_name=record["full_name"],
                password_hash=record["password_hash"],
                role=record["role"],
            )
        return None

    async def create_user(self, user_data: dict) -> UserDB:
        user_id = str(uuid4())
        query = f"""
        CREATE (u:User:{user_data["role"]} {{
            id: $id,
            email: $email,
            full_name: $full_name,
            password_hash: $password_hash,
            role: $role
        }})
        RETURN u.id as id, u.email as email, u.full_name as full_name, u.role as role
        """
        result = await self.driver.execute_query(
            query,
            id=user_id,
            email=user_data["email"],
            full_name=user_data["full_name"],
            password_hash=user_data["password_hash"],
            role=user_data["role"],
        )
        record = result.records[0]
        return UserDB(
            id=record["id"],
            email=record["email"],
            full_name=record["full_name"],
            password_hash=user_data["password_hash"],
            role=record["role"],
        )

    async def filter_users(self, filters: UserFilter) -> dict:
        match_clause = "MATCH (u:User)"
        where_clauses = []
        params = {}

        if filters.email:
            where_clauses.append("toLower(u.email) CONTAINS toLower($email)")
            params["email"] = filters.email

        if filters.full_name:
            where_clauses.append("toLower(u.full_name) CONTAINS toLower($full_name)")
            params["full_name"] = filters.full_name

        if filters.role:
            where_clauses.append("u.role = $role")
            params["role"] = filters.role

        where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        sort_field = filters.sort_by.value if filters.sort_by else "email"
        sort_order = filters.sort_order.value if filters.sort_order else "ASC"
        order_by = f"ORDER BY u.{sort_field} {sort_order}"

        count_query = f"""
            {match_clause}
            {where_clause}
            RETURN count(u) as total
        """
        count_result = await self.driver.execute_query(count_query, params)
        total = count_result.records[0]["total"] if count_result.records else 0

        data_query = f"""
            {match_clause}
            {where_clause}
            {order_by}
            SKIP $offset
            LIMIT $limit
            RETURN u.id as id, u.email as email, u.full_name as full_name, u.role as role
        """
        params["offset"] = filters.offset or 0
        params["limit"] = filters.limit or 50

        result = await self.driver.execute_query(data_query, params)

        items = []
        for record in result.records:
            items.append(
                {
                    "id": record["id"],
                    "email": record["email"],
                    "full_name": record["full_name"],
                    "role": record["role"],
                }
            )

        return {"total": total, "items": items}

    async def delete_user(self, user_id: str) -> bool:
        query = """
        MATCH (u:User {id: $user_id})
        DELETE u
        RETURN COUNT(u) as deleted
        """
        result = await self.driver.execute_query(query, user_id=user_id)
        deleted = result.records[0]["deleted"] if result.records else 0
        return deleted > 0
