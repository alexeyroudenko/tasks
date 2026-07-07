from app.graph.renderer import Renderer
from app.graph.task import Task


def make_task(graph, **attrs):
    task = Task.load(graph, **attrs)

    return task


def build_renderer(graph):
    """Renderer over three tasks: epic <- feature <- task, without hitting Neo4j."""
    epic = make_task(graph, id="e1", title="Epic", type="epic", status="todo")
    feature = make_task(graph, id="f1", title="Feature", type="feature", status="in_progress")
    task = make_task(graph, id="t1", title="Task", type="task", status="done")

    related = {
        ("f1", "child_of"): [epic],
        ("t1", "child_of"): [feature],
        ("f1", "parent_of"): [task],
    }

    for t in (epic, feature, task):
        t.related = lambda name, _id=t.id: related.get((_id, name), [])  # type: ignore[method-assign]

    renderer = Renderer(graph)
    renderer._tasks = [epic, feature, task]

    return renderer


def test_nodes_payload(graph):
    renderer = build_renderer(graph)
    nodes = renderer.nodes()

    assert [n["id"] for n in nodes] == ["e1", "f1", "t1"]
    assert nodes[0]["type"] == "Epic"
    assert nodes[0]["icon"] == "collection"
    assert nodes[2]["status"] == "green-500"


def test_edges_use_node_indices(graph):
    renderer = build_renderer(graph)
    edges = renderer.edges()

    assert {"source": 1, "target": 0, "label": "Child Of"} in edges
    assert {"source": 2, "target": 1, "label": "Child Of"} in edges


def test_groups_contain_feature_children(graph):
    renderer = build_renderer(graph)

    assert renderer.groups() == [{"leaves": [2]}]


def test_constraints_order_type_tiers(graph):
    renderer = build_renderer(graph)
    constraints = renderer.constraints()

    # epic above feature, feature above task
    assert {"axis": "y", "left": 0, "right": 1, "gap": 150} in constraints
    assert {"axis": "y", "left": 1, "right": 2, "gap": 150} in constraints


def test_to_dict_shape(graph):
    payload = build_renderer(graph).to_dict()

    assert set(payload.keys()) == {"nodes", "edges", "groups", "constraints"}
