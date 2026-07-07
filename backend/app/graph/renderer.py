from __future__ import annotations

from typing import Any

from app.graph import task as task_module
from app.graph.graph import Graph
from app.graph.task import RELATIONSHIPS, Task

# Heroicon names per task type; the frontend maps names to SVG paths
ICON_FOR_TYPE = {
    "idea": "light-bulb",
    "goal": "flag",
    "epic": "collection",
    "feature": "puzzle",
    "task": "clipboard-list",
    "bug": "exclamation-circle",
}

COLOR_FOR_TYPE = {
    "idea": "purple-500",
    "goal": "red-500",
    "epic": "pink-500",
    "feature": "blue-500",
    "task": "gray-500",
    "bug": "red-600",
}

COLOR_FOR_STATUS = {
    "todo": "gray-400",
    "in_progress": "blue-500",
    "review": "yellow-500",
    "done": "green-500",
}


def titleize(value: str) -> str:
    return value.replace("_", " ").title()


class Renderer:
    """Build the D3-ready payload: nodes, edges, groups and layout constraints."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self._tasks: list[Task] | None = None

    @property
    def tasks(self) -> list[Task]:
        if self._tasks is None:
            tasks = self.graph.tasks()
            # Stable order: by type (idea first), then title
            tasks.sort(
                key=lambda t: (task_module.TYPES.index(t.type), t.title or "")
            )
            self._tasks = tasks

        return self._tasks

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": self.nodes(),
            "edges": self.edges(),
            "groups": self.groups(),
            "constraints": self.constraints(),
        }

    def nodes(self) -> list[dict[str, Any]]:
        return [
            {
                "id": task.id,
                "label": task.title,
                "icon": ICON_FOR_TYPE[task.type],
                "color": COLOR_FOR_TYPE[task.type],
                "type": titleize(task.type),
                "status": COLOR_FOR_STATUS[task.status],
            }
            for task in self.tasks
        ]

    def edges(self) -> list[dict[str, Any]]:
        index = {task.id: i for i, task in enumerate(self.tasks)}
        stored_types = [name for name, inverse in RELATIONSHIPS.items() if inverse is None]

        edges = []
        for task in self.tasks:
            for relationship in stored_types:
                for other in task.related(relationship):
                    if other.id not in index:
                        continue
                    edges.append(
                        {
                            "source": index[task.id],
                            "target": index[other.id],
                            "label": titleize(relationship),
                        }
                    )

        return edges

    def groups(self) -> list[dict[str, Any]]:
        index = {task.id: i for i, task in enumerate(self.tasks)}

        groups = []
        for task in self.tasks:
            if task.type != "feature":
                continue
            children = [
                index[child.id]
                for child in task.related("parent_of")
                if child.id in index
            ]
            if children:
                groups.append({"leaves": children})

        return groups

    def constraints(self) -> list[dict[str, Any]]:
        """Vertical ordering between consecutive task type tiers."""
        by_type: dict[str, list[int]] = {}
        for i, task in enumerate(self.tasks):
            by_type.setdefault(task.type, []).append(i)

        tiers = [by_type[t] for t in task_module.TYPES if t in by_type]

        constraints = []
        for upper, lower in zip(tiers, tiers[1:]):
            for left in upper:
                for right in lower:
                    constraints.append(
                        {"axis": "y", "left": left, "right": right, "gap": 150}
                    )

        return constraints
