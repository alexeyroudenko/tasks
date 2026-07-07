from __future__ import annotations

from typing import TYPE_CHECKING, Any

from neo4j import Driver, GraphDatabase

from app.config import settings
from app.graph.dsl import DSL

if TYPE_CHECKING:
    from app.graph.task import Task

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )

    return _driver


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


class Graph:
    """A logical graph, one per project.

    The original app used one RedisGraph key per project; in Neo4j all nodes
    live in one database and are scoped by a `graph` property (the DSL adds it
    to every labeled node pattern automatically).
    """

    def __init__(self, name: str, driver: Driver | None = None) -> None:
        self.name = str(name)
        self.driver = driver or get_driver()

    def query(self, cypher: str) -> list[Any]:
        with self.driver.session() as session:
            return list(session.run(cypher))

    def dsl(self) -> DSL:
        return DSL(self)

    def match(self, name: str, label: str | None = None, **attributes: Any) -> DSL:
        return self.dsl().match(name, label, **attributes)

    def merge(self, name: str, label: str | None = None, **attributes: Any) -> DSL:
        return self.dsl().merge(name, label, **attributes)

    def tasks(self) -> list[Task]:
        from app.graph.task import Task

        return [
            Task.from_record(self, row["n"])
            for row in self.match("n", "Task").return_("n")
        ]

    def delete_all(self) -> None:
        """Remove every node (and attached edges) belonging to this graph."""
        self.query(f"MATCH (n {{graph: '{self.name}'}}) DETACH DELETE n")

    def __repr__(self) -> str:
        return f"#<Graph name={self.name}>"
