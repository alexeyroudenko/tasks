from unittest.mock import MagicMock

import pytest

from app.graph.graph import Graph


@pytest.fixture
def graph() -> Graph:
    """A Graph whose queries are captured instead of hitting Neo4j."""
    fake = MagicMock(spec=Graph)
    fake.name = "g1"
    fake.query.return_value = []

    real = Graph.__new__(Graph)
    real.name = "g1"
    real.driver = None
    real.query = fake.query  # type: ignore[method-assign]

    return real
