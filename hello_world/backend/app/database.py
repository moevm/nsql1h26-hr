import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        if self.driver:
            self.driver.close()

    def create_greeting(self, message: str):
        with self.driver.session() as session:
            session.run("CREATE (g:Greeting {message: $message})", message=message)

    def get_greetings(self):
        with self.driver.session() as session:
            result = session.run("MATCH (g:Greeting) RETURN g.message AS message")
            return [record["message"] for record in result]
db = Neo4jConnection()