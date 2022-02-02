from unittest.mock import Mock

import pytest

from galo_startup_commands import DependencyGraphNodeStartupCommand, to_graph


def test_empty_collection() -> None:
    assert to_graph([]) == {}


def test_single_command_collection() -> None:
    command = DependencyGraphNodeStartupCommand(Mock())
    assert to_graph([command]) == {command: set()}


def test_two_independent_commands() -> None:
    command1 = DependencyGraphNodeStartupCommand(Mock())
    command2 = DependencyGraphNodeStartupCommand(Mock())
    assert to_graph([command1, command2]) == {command1: set(), command2: set()}


def test_command2_after_command1() -> None:
    command1 = DependencyGraphNodeStartupCommand(Mock(), name="command1")
    command2 = DependencyGraphNodeStartupCommand(Mock(), after=["command1"])
    assert to_graph([command1, command2]) == {command1: set(), command2: {command1}}


def test_command1_before_command2() -> None:
    command1 = DependencyGraphNodeStartupCommand(Mock(), before=["command2"])
    command2 = DependencyGraphNodeStartupCommand(Mock(), name="command2")
    assert to_graph([command1, command2]) == {command1: set(), command2: {command1}}


def test_command1_has_order_less_than_command2() -> None:
    command1 = DependencyGraphNodeStartupCommand(Mock(), order=1)
    command2 = DependencyGraphNodeStartupCommand(Mock(), order=2)
    assert to_graph([command1, command2]) == {command1: set(), command2: {command1}}


def test_command_after_another_non_existent_command() -> None:
    command = DependencyGraphNodeStartupCommand(Mock(), after=["non_existent_command"])
    with pytest.raises(Exception):
        to_graph([command])


def test_command_before_another_non_existent_command() -> None:
    command = DependencyGraphNodeStartupCommand(Mock(), before=["non_existent_command"])
    with pytest.raises(Exception):
        to_graph([command])
