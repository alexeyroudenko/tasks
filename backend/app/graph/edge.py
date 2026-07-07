from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.graph.graph import Graph

if TYPE_CHECKING:
    from app.graph.node import Node

EDGE_TYPES = ("related_to", "blocked_by", "child_of")


class Edge:
    """A directed relationship between two nodes."""

    def __init__(
        self,
        graph: Graph,
        from_node: Node | None = None,
        type: str = "related_to",
        to_node: Node | None = None,
    ) -> None:
        self.graph = graph
        self.from_node = from_node
        self.type = type
        self.to_node = to_node
        self._persisted = False
        self._destroyed = False

    @classmethod
    def load(cls, graph: Graph, from_node: Node, type: str, to_node: Node) -> Edge:
        edge = cls(graph, from_node=from_node, type=type, to_node=to_node)
        edge._persisted = True

        return edge

    @classmethod
    def where(
        cls,
        graph: Graph,
        node_class: type[Node],
        from_id: str | None = None,
        type: str | None = None,
        to_id: str | None = None,
    ) -> list[Edge]:
        """Find edges, optionally filtered by endpoints and type."""
        from_attrs: dict[str, Any] = {"id": from_id} if from_id else {}
        to_attrs: dict[str, Any] = {"id": to_id} if to_id else {}

        rows = (
            graph.match("n", node_class.label(), **from_attrs)
            .to("r", type)
            .match("m", node_class.label(), **to_attrs)
            .return_("n", "m", t="type(r)")
        )

        return [
            cls.load(
                graph,
                from_node=node_class.from_record(graph, row["n"]),
                type=row["t"],
                to_node=node_class.from_record(graph, row["m"]),
            )
            for row in rows
        ]

    @classmethod
    def find(cls, graph: Graph, node_class: type[Node], **kwargs: Any) -> Edge | None:
        edges = cls.where(graph, node_class, **kwargs)

        return edges[0] if edges else None

    def validate(self) -> list[str]:
        errors = []
        if self.from_node is None or self.from_node.id is None:
            errors.append("from_node is required")
        if self.to_node is None or self.to_node.id is None:
            errors.append("to_node is required")
        if self.type not in EDGE_TYPES:
            errors.append(f"type must be one of {EDGE_TYPES}")

        return errors

    @property
    def persisted(self) -> bool:
        return self._persisted

    def save(self) -> bool:
        if self.validate():
            return False

        (
            self.graph.match("n", self.from_node.label(), id=self.from_node.id)
            .match("m", self.to_node.label(), id=self.to_node.id)
            .merge("n")
            .to("r", self.type)
            .merge("m")
            .execute()
        )

        self._persisted = True

        return True

    def destroy(self) -> bool:
        if self._destroyed or self.validate():
            return False

        (
            self.graph.match("n", self.from_node.label(), id=self.from_node.id)
            .to("r", self.type)
            .match("m", self.to_node.label(), id=self.to_node.id)
            .delete("r")
            .execute()
        )

        self._destroyed = True
        self._persisted = False

        return True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Edge)
            and self.type == other.type
            and self.from_node == other.from_node
            and self.to_node == other.to_node
        )

    def __repr__(self) -> str:
        return f"#<Edge {self.from_node!r} -[{self.type}]-> {self.to_node!r}>"
