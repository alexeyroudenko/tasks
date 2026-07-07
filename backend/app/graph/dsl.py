"""Chainable Cypher query builder, ported from code-red's ActiveRecord-style DSL.

Example:

    graph.match("n", "Task", id="x").to("r", "blocked_by").match("m", "Task").delete("r")

renders to:

    MATCH (n:Task {id: 'x'}) -[r:blocked_by]-> (m:Task) DELETE r
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.graph.graph import Graph


def format_value(value: Any) -> str:
    """Render a Python value as a single-quoted Cypher string literal."""
    if isinstance(value, (date, datetime)):
        value = value.isoformat()

    escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")

    return f"'{escaped}'"


class Clause(list):
    """Simple clause: elements joined with spaces."""

    def to_query(self) -> str:
        return " ".join(self)


class ReturnClause(Clause):
    """Return clause: elements joined with commas."""

    def to_query(self) -> str:
        return ", ".join(self)


class MatchClause(Clause):
    """Match/merge clause: nodes joined with commas, except around relationship arrows.

    ["(n)", "(m)"] renders to "(n), (m)"
    ["(n)", "-[r]->", "(m)"] renders to "(n) -[r]-> (m)"
    """

    def to_query(self) -> str:
        parts: list[str] = []
        for index, element in enumerate(self):
            if index > 0:
                previous = self[index - 1]
                separator = " " if previous.endswith(">") or element.startswith("-") else ", "
                parts.append(separator)
            parts.append(element)

        return "".join(parts)


class DSL:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.clauses: dict[str, Clause] = {
            "match": MatchClause(),
            "merge": MatchClause(),
            "return": ReturnClause(),
            "delete": Clause(),
            "set": Clause(),
        }
        # Ordered set of variable names referenced in the query
        self.names: list[str] = []
        self._target: str | None = None

    def _add_name(self, name: str) -> None:
        if name not in self.names:
            self.names.append(name)

    def _pattern(self, name: str, label: str | None, attributes: dict[str, Any]) -> str:
        rendered = name
        if label:
            rendered += f":{label}"
        if attributes:
            pairs = ", ".join(f"{k}: {format_value(v)}" for k, v in attributes.items())
            rendered += f" {{{pairs}}}"

        return f"({rendered})"

    def match(self, name: str, label: str | None = None, **attributes: Any) -> DSL:
        self._add_name(name)

        # Scope labeled node patterns to this graph
        if label:
            attributes = {"graph": self.graph.name, **attributes}

        self.clauses["match"].append(self._pattern(name, label, attributes))
        self._target = "match"

        return self

    def merge(self, name: str, label: str | None = None, **attributes: Any) -> DSL:
        self._add_name(name)

        if label:
            attributes = {"graph": self.graph.name, **attributes}

        self.clauses["merge"].append(self._pattern(name, label, attributes))
        self._target = "merge"

        return self

    def to(self, name: str, label: str | None = None) -> DSL:
        if self._target is None:
            raise ValueError("method `to` without preceding `match` or `merge` not allowed")

        rendered = name
        if label:
            rendered += f":{label}"

        self.clauses[self._target].append(f"-[{rendered}]->")

        return self

    def return_(self, *names: str, **aliases: str) -> DSL:
        for name in names:
            self._add_name(name)
            self.clauses["return"].append(name)

        for alias, expression in aliases.items():
            self._add_name(alias)
            self.clauses["return"].append(f"{expression} AS {alias}")

        return self

    def delete(self, *names: str) -> DSL:
        for name in names:
            self._add_name(name)

        self.clauses["delete"].append(", ".join(names))

        return self

    def set(self, **attributes: Any) -> DSL:
        assignments = []
        for name in self.names:
            for key, value in attributes.items():
                if value is None:
                    assignments.append(f"{name}.{key} = null")
                else:
                    assignments.append(f"{name}.{key} = {format_value(value)}")

        self.clauses["set"].append(", ".join(assignments))

        return self

    def to_cypher(self) -> str:
        parts = []
        for keyword, clause in self.clauses.items():
            if clause:
                parts.append(f"{keyword.upper()} {clause.to_query()}")

        return " ".join(parts)

    def execute(self) -> list[dict[str, Any]]:
        records = self.graph.query(self.to_cypher())

        rows = []
        for record in records:
            row = {}
            for name in self.names:
                if name not in record.keys():
                    continue
                value = record[name]
                # Unwrap graph entities (nodes/relationships) into plain dicts
                row[name] = dict(value.items()) if hasattr(value, "items") else value
            rows.append(row)

        return rows

    def __iter__(self):
        return iter(self.execute())

    def first(self) -> dict[str, Any] | None:
        results = self.execute()

        return results[0] if results else None
