from unittest.mock import AsyncMock, call

import pytest

from galo_startup_commands import AsyncGeneratorFunctionStartupCommand


def test_startup() -> None:
    async def function():
        await mock.startup_async()
        yield

    mock = AsyncMock()
    command = AsyncGeneratorFunctionStartupCommand(function)

    with pytest.raises(Exception):
        command.startup()
    mock.startup_async.assert_not_called()


def test_shutdown() -> None:
    async def function():
        await mock.startup_async()
        yield
        await mock.shutdown_async()

    mock = AsyncMock()
    command = AsyncGeneratorFunctionStartupCommand(function)

    with pytest.raises(Exception):
        command.shutdown()
    mock.startup_async.assert_not_called()
    mock.shutdown_async.assert_not_called()


@pytest.mark.asyncio
async def test_startup_async_and_shutdown_async() -> None:
    async def function():
        await mock.startup_async()
        yield
        await mock.shutdown_async()

    mock = AsyncMock()
    command = AsyncGeneratorFunctionStartupCommand(function)

    await command.startup_async()
    mock.assert_has_calls(
        [
            call.startup_async(),
        ]
    )

    await command.shutdown_async()
    mock.assert_has_calls(
        [
            call.startup_async(),
            call.shutdown_async(),
        ]
    )


@pytest.mark.asyncio
async def test_startup_async_twice() -> None:
    async def function():
        await mock.startup_async()
        yield

    mock = AsyncMock()
    command = AsyncGeneratorFunctionStartupCommand(function)
    await command.startup_async()
    await command.startup_async()
    mock.startup_async.assert_called_once_with()


@pytest.mark.asyncio
async def test_shutdown_async_before_startup_async() -> None:
    async def function():
        await mock.startup_async()
        yield
        await mock.shutdown_async()

    mock = AsyncMock()
    command = AsyncGeneratorFunctionStartupCommand(function)
    await command.shutdown_async()
    mock.startup_async.assert_not_called()
    mock.shutdown_async.assert_not_called()


@pytest.mark.asyncio
async def test_shutdown_with_exception() -> None:
    async def function():
        try:
            yield
        except Exception as e:
            await mock.shutdown_async(e)

    exception = Exception()
    mock = AsyncMock()
    command = AsyncGeneratorFunctionStartupCommand(function)
    await command.startup_async()
    await command.shutdown_async(exception)
    mock.shutdown_async.assert_called_once_with(exception)
