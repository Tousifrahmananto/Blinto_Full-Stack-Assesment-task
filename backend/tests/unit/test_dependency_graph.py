import pytest

from app.algorithms.dependency_graph import prerequisite_order


def test_iterative_traversal_handles_long_chain_and_detects_back_edge():
    graph = {movie: [movie + 1] for movie in range(2000)}
    assert prerequisite_order(graph, 0) == list(range(2000, 0, -1))
    graph[2000] = [1]
    with pytest.raises(ValueError, match="Circular"):
        prerequisite_order(graph, 0)
