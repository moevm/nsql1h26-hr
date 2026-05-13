from neo4j import AsyncDriver


class AdminRepository:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def erase_all(self) -> None:
        async with self.driver.session() as session:
            await session.run("""
            MATCH (n)
            DETACH DELETE n
            """)

    async def is_empty(self) -> bool:
        async with self.driver.session() as session:
            result = await session.run("""
            MATCH (n)
            RETURN COUNT(n) AS count
            """)
            resp = await result.single()
            return resp["count"] == 0
