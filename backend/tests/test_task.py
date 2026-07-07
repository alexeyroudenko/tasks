import pytest

from app.graph.task import Task


def test_defaults(graph):
    task = Task(graph, title="Test")

    assert task.status == "todo"
    assert task.type == "task"
    assert not task.persisted


def test_validate_requires_title(graph):
    task = Task(graph, title=None)

    assert "title is required" in task.validate()


def test_validate_status(graph):
    task = Task(graph, title="Test", status="bogus")

    assert any("status" in e for e in task.validate())


def test_save_generates_id_and_persists(graph):
    task = Task(graph, title="Test")

    assert task.save()
    assert task.id is not None
    assert task.created_at is not None
    assert task.persisted

    cypher = graph.query.call_args[0][0]
    assert cypher.startswith(f"MERGE (n:Task {{graph: 'g1', id: '{task.id}'}})")
    assert "n.title = 'Test'" in cypher


def test_save_invalid_returns_false(graph):
    task = Task(graph, title=None)

    assert not task.save()
    graph.query.assert_not_called()


def test_destroy_unpersisted_returns_false(graph):
    task = Task(graph, title="Test")

    assert not task.destroy()


def test_invert_stored_type_passthrough():
    assert Task.invert("a", "blocked_by", "b") == ("a", "blocked_by", "b")
    assert Task.invert("a", "related_to", "b") == ("a", "related_to", "b")


def test_invert_inverse_relationship():
    assert Task.invert("a", "blocks", "b") == ("b", "blocked_by", "a")
    assert Task.invert("a", "parent_of", "b") == ("b", "child_of", "a")


def test_related_unknown_relationship_raises(graph):
    task = Task(graph, title="Test")

    with pytest.raises(ValueError):
        task.related("nonsense")


def test_related_unpersisted_returns_empty(graph):
    task = Task(graph, title="Test")

    assert task.related("blocked_by") == []
