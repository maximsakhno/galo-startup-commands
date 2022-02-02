from unittest.mock import AsyncMock, Mock

import pytest

from galo_startup_commands import DependencyGraphNodeStartupCommand


def test_get_name_when_name_is_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock())
    assert command.name is None


def test_get_name_when_name_is_not_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock(), name="test")
    assert command.name == "test"


def test_get_after_when_after_is_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock())
    assert command.after is None


def test_get_after_when_after_is_not_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock(), after=[])
    assert command.after == []


def test_get_before_when_before_is_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock())
    assert command.before is None


def test_get_before_when_before_is_not_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock(), before=[])
    assert command.before == []


def test_get_order_when_order_is_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock())
    assert command.order is None


def test_get_order_when_order_is_not_none() -> None:
    command = DependencyGraphNodeStartupCommand(Mock(), order=0)
    assert command.order == 0


def test_startup() -> None:
    mock = Mock()
    command = DependencyGraphNodeStartupCommand(mock)
    command.startup()
    mock.startup.assert_called_once_with()


def test_shutdown() -> None:
    mock = Mock()
    command = DependencyGraphNodeStartupCommand(mock)
    command.shutdown()
    mock.shutdown.assert_called_once_with(None)


def test_shutdown_with_exception() -> None:
    exception = Exception()
    mock = Mock()
    command = DependencyGraphNodeStartupCommand(mock)
    command.shutdown(exception)
    mock.shutdown.assert_called_once_with(exception)


@pytest.mark.asyncio
async def test_startup_async() -> None:
    mock = AsyncMock()
    command = DependencyGraphNodeStartupCommand(mock)
    await command.startup_async()
    mock.startup_async.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_shutdown_async() -> None:
    mock = AsyncMock()
    command = DependencyGraphNodeStartupCommand(mock)
    await command.shutdown_async()
    mock.shutdown_async.assert_awaited_once_with(None)


@pytest.mark.asyncio
async def test_shutdown_async_with_exception() -> None:
    exception = Exception()
    mock = AsyncMock()
    command = DependencyGraphNodeStartupCommand(mock)
    await command.shutdown_async(exception)
    mock.shutdown_async.assert_awaited_once_with(exception)
