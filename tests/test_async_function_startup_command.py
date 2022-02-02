from unittest.mock import AsyncMock

import pytest

from galo_startup_commands import AsyncFunctionStartupCommand


def test_startup() -> None:
    mock = AsyncMock()
    command = AsyncFunctionStartupCommand(mock)
    with pytest.raises(Exception):
        command.startup()
    mock.assert_not_awaited()


def test_shutdown() -> None:
    mock = AsyncMock()
    command = AsyncFunctionStartupCommand(mock)
    command.shutdown()
    mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_startup_async() -> None:
    mock = AsyncMock()
    command = AsyncFunctionStartupCommand(mock)
    await command.startup_async()
    mock.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_shutdown_async() -> None:
    mock = AsyncMock()
    command = AsyncFunctionStartupCommand(mock)
    await command.shutdown_async()
    mock.assert_not_awaited()
