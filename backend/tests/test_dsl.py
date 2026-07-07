from datetime import date

import pytest

from app.graph.dsl import DSL, MatchClause, format_value


def test_match_single_node(graph):
    query = DSL(graph).match("n", "Task").return_("n")

    assert query.to_cypher() == "MATCH (n:Task {graph: 'g1'}) RETURN n"


def test_match_with_attributes(graph):
    query = DSL(graph).match("n", "Task", id="abc").return_("n")

    assert query.to_cypher() == "MATCH (n:Task {graph: 'g1', id: 'abc'}) RETURN n"


def test_match_relationship_pattern(graph):
    query = (
        DSL(graph)
        .match("n", "Task", id="x")
        .to("r", "blocked_by")
        .match("m", "Task")
        .delete("r")
    )

    assert query.to_cypher() == (
        "MATCH (n:Task {graph: 'g1', id: 'x'}) -[r:blocked_by]-> "
        "(m:Task {graph: 'g1'}) DELETE r"
    )


def test_match_multiple_nodes_separated_by_comma(graph):
    query = (
        DSL(graph)
        .match("n", "Task", id="a")
        .match("m", "Task", id="b")
        .merge("n")
        .to("r", "child_of")
        .merge("m")
    )

    assert query.to_cypher() == (
        "MATCH (n:Task {graph: 'g1', id: 'a'}), (m:Task {graph: 'g1', id: 'b'}) "
        "MERGE (n) -[r:child_of]-> (m)"
    )


def test_merge_with_set(graph):
    query = DSL(graph).merge("n", "Task", id="1").set(title="Hello", status="todo")

    assert query.to_cypher() == (
        "MERGE (n:Task {graph: 'g1', id: '1'}) "
        "SET n.title = 'Hello', n.status = 'todo'"
    )


def test_set_none_renders_null(graph):
    query = DSL(graph).merge("n", "Task", id="1").set(deadline=None)

    assert query.to_cypher() == (
        "MERGE (n:Task {graph: 'g1', id: '1'}) SET n.deadline = null"
    )


def test_return_with_alias(graph):
    query = DSL(graph).match("n", "Task").return_("n", t="type(r)")

    assert query.to_cypher() == "MATCH (n:Task {graph: 'g1'}) RETURN n, type(r) AS t"


def test_to_without_match_or_merge_raises(graph):
    with pytest.raises(ValueError):
        DSL(graph).to("r", "blocked_by")


def test_format_value_escapes_quotes():
    assert format_value("it's") == "'it\\'s'"


def test_format_value_escapes_backslashes():
    assert format_value("a\\b") == "'a\\\\b'"


def test_format_value_dates():
    assert format_value(date(2026, 7, 8)) == "'2026-07-08'"


def test_match_clause_separators():
    clause = MatchClause(["(n)", "-[r]->", "(m)", "(o)"])

    assert clause.to_query() == "(n) -[r]-> (m), (o)"
