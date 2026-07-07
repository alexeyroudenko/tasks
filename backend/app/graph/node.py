from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar

from app.graph.graph import Graph


class ValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class Node:
    """Base class for graph nodes, persisted via MERGE + SET (upsert)."""

    # Attribute names persisted to the graph, extended by subclasses
    attributes: ClassVar[tuple[str, ...]] = ("id", "created_at", "updated_at")

    def __init__(self, graph: Graph, **attrs: Any) -> None:
        self.graph = graph
        self._persisted = False
        self._destroyed = False

        for name in self.attributes:
            setattr(self, name, attrs.pop(name, None))

        # Ignore non-attribute keys coming back from the database (e.g. `graph`)
        attrs.pop("graph", None)

    @classmethod
    def label(cls) -> str:
        return cls.__name__

    @classmethod
    def load(cls, graph: Graph, **attrs: Any) -> Node:
        node = cls(graph, **attrs)
        node._persisted = True

        return node

    @classmethod
    def find(cls, graph: Graph, id: str) -> Node | None:
        row = graph.match("n", cls.label(), id=id).return_("n").first()
        if row is None:
            return None

        return cls.load(graph, **row["n"])

    def validate(self) -> list[str]:
        return []

    def to_attributes(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.attributes}

    @property
    def persisted(self) -> bool:
        return self._persisted

    @property
    def destroyed(self) -> bool:
        return self._destroyed

    def save(self) -> bool:
        errors = self.validate()
        if errors:
            return False

        if self.id is None:
            self.id = str(uuid.uuid4())

        now = datetime.now(UTC)
        if self.created_at is None:
            self.created_at = now
        self.updated_at = now

        (
            self.graph.merge("n", self.label(), id=self.id)
            .set(**{k: v for k, v in self.to_attributes().items() if k != "id"})
            .execute()
        )

        self._persisted = True

        return True

    def update(self, **attrs: Any) -> bool:
        for name, value in attrs.items():
            if name in self.attributes:
                setattr(self, name, value)

        return self.save()

    def destroy(self) -> bool:
        if self._destroyed or not self._persisted:
            return False

        (
            self.graph.match("n", self.label(), id=self.id)
            .delete("n")
            .execute()
        )

        self._destroyed = True
        self._persisted = False

        return True

    def reload(self) -> bool:
        if not self._persisted:
            return False

        row = self.graph.match("n", self.label(), id=self.id).return_("n").first()
        if row is None:
            return False

        for name, value in row["n"].items():
            if name in self.attributes:
                setattr(self, name, value)

        return True

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self))
            and self._persisted
            and other.id == self.id
        )

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{k}={v}" for k, v in self.to_attributes().items() if v is not None
        )

        return f"#<{type(self).__name__} {attrs}>"
