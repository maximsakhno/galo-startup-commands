from unittest.mock import Mock

import pytest

from galo_startup_commands import FunctionStartupCommand


def test_startup() -> None:
    mock = Mock()
    command = FunctionStartupCommand(mock)
    command.startup()
    mock.assert_called_once_with()


def test_shutdown() -> None:
    command = FunctionStartupCommand(Mock())
    command.shutdown()


@pytest.mark.asyncio
async def test_startup_async() -> None:
    mock = Mock()
    command = FunctionStartupCommand(mock)
    await command.startup_async()
    mock.assert_called_once_with()


@pytest.mark.asyncio
async def test_shutdown_async() -> None:
    command = FunctionStartupCommand(Mock())
    await command.shutdown_async()
