from typing import Dict, Set

import pytest

from galo_startup_commands import GraphCycleException, topological_sort


def test_empty_graph() -> None:
    graph: Dict[str, Set[str]] = {}
    assert list(topological_sort(graph)) == []


def test_single_node_graph() -> None:
    graph: Dict[str, Set[str]] = {"a": set()}
    assert list(topological_sort(graph)) == ["a"]


def test_single_node_cyclic_graph() -> None:
    graph: Dict[str, Set[str]] = {"a": {"a"}}
    with pytest.raises(GraphCycleException) as exc_info:
        list(topological_sort(graph))

    assert list(exc_info.value.cycle) == ["a"]


def test_node_a_after_node_b() -> None:
    graph: Dict[str, Set[str]] = {"a": {"b"}}
    assert list(topological_sort(graph)) == ["b", "a"]


def test_two_node_cyclic_graph() -> None:
    graph: Dict[str, Set[str]] = {"a": {"b"}, "b": {"a"}}
    with pytest.raises(GraphCycleException) as exc_info:
        list(topological_sort(graph))

    assert exc_info.value.cycle in (["a", "b"], ["b", "a"])


def test_tree() -> None:
    graph: Dict[str, Set[str]] = {"c": {"a", "b"}}
    result = list(topological_sort(graph))
    assert result.index("a") < result.index("c") and result.index("b") < result.index("c")


def test_forest() -> None:
    graph: Dict[str, Set[str]] = {"c": {"b", "a"}, "f": {"e", "d"}}
    result = list(topological_sort(graph))
    assert (
        result.index("a") < result.index("c")
        and result.index("b") < result.index("c")
        and result.index("d") < result.index("f")
        and result.index("e") < result.index("f")
    )


def test_graph_without_edges() -> None:
    graph: Dict[str, Set[str]] = {"a": set(), "b": set(), "c": set()}
    assert set(topological_sort(graph)) == {"a", "b", "c"}


def test_three_node_cyclic_graph() -> None:
    graph: Dict[str, Set[str]] = {"c": {"a"}, "b": {"c"}, "a": {"b"}}
    with pytest.raises(GraphCycleException) as exc_info:
        list(topological_sort(graph))

    assert exc_info.value.cycle in (["a", "b", "c"], ["b", "c", "a"], ["c", "a", "b"])
