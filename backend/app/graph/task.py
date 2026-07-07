from __future__ import annotations

from typing import ClassVar

from app.graph.edge import Edge
from app.graph.node import Node

STATUSES = ("todo", "in_progress", "review", "done")
TYPES = ("idea", "goal", "epic", "feature", "task", "bug")

# Stored relationship types map to None; inverse pseudo-relationships map to
# the stored type they invert (resolved in code, never persisted).
RELATIONSHIPS: dict[str, str | None] = {
    "blocked_by": None,
    "blocks": "blocked_by",
    "child_of": None,
    "parent_of": "child_of",
    "related_to": None,
}


class Task(Node):
    attributes: ClassVar[tuple[str, ...]] = (
        "id",
        "title",
        "description",
        "deadline",
        "status",
        "type",
        "user_id",
        "created_at",
        "updated_at",
    )

    def __init__(self, graph, **attrs):
        attrs.setdefault("status", "todo")
        attrs.setdefault("type", "task")
        super().__init__(graph, **attrs)

    def validate(self) -> list[str]:
        errors = []
        if not self.title:
            errors.append("title is required")
        if self.status not in STATUSES:
            errors.append(f"status must be one of {STATUSES}")
        if self.type not in TYPES:
            errors.append(f"type must be one of {TYPES}")

        return errors

    def related(self, relationship: str) -> list[Task]:
        """Tasks connected via a relationship name, including inverse ones.

        `task.related("blocked_by")` returns tasks this task is blocked by;
        `task.related("blocks")` returns tasks that this task blocks.
        """
        if relationship not in RELATIONSHIPS:
            raise ValueError(f"unknown relationship {relationship!r}")

        if not self.persisted:
            return []

        inverse_of = RELATIONSHIPS[relationship]

        if inverse_of:
            edges = Edge.where(self.graph, Task, type=inverse_of, to_id=self.id)

            return [edge.from_node for edge in edges]

        edges = Edge.where(self.graph, Task, from_id=self.id, type=relationship)

        return [edge.to_node for edge in edges]

    @staticmethod
    def invert(from_id: str, type: str, to_id: str) -> tuple[str, str, str]:
        """Normalize an inverse relationship into its stored direction.

        (a, "blocks", b) becomes (b, "blocked_by", a).
        """
        inverse_of = RELATIONSHIPS.get(type)

        if inverse_of:
            return to_id, inverse_of, from_id

        return from_id, type, to_id
