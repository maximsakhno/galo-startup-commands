from unittest.mock import AsyncMock, Mock, call

import pytest

from galo_startup_commands import SequenceStartupCommand


def test_startup_and_shutdown() -> None:
    mock = Mock()
    command = SequenceStartupCommand([mock.command1, mock.command2])
    command.startup()
    mock.assert_has_calls(
        [
            call.command1.startup(),
            call.command2.startup(),
        ]
    )
    command.shutdown()
    mock.assert_has_calls(
        [
            call.command1.startup(),
            call.command2.startup(),
            call.command2.shutdown(None),
            call.command1.shutdown(None),
        ]
    )


def test_startup_with_exception() -> None:
    exception = Exception()
    mock = Mock()
    mock.command2.startup.side_effect = exception
    command = SequenceStartupCommand([mock.command1, mock.command2])
    with pytest.raises(Exception):
        command.startup()
    mock.assert_has_calls(
        [
            call.command1.startup(),
            call.command2.startup(),
            call.command1.shutdown(exception),
        ]
    )


def test_shutdown_with_exception() -> None:
    exception = Exception()
    mock = Mock()
    mock.command2.shutdown.side_effect = exception
    command = SequenceStartupCommand([mock.command1, mock.command2])
    command.startup()
    with pytest.raises(Exception):
        command.shutdown()
    mock.assert_has_calls(
        [
            call.command1.startup(),
            call.command2.startup(),
            call.command2.shutdown(None),
            call.command1.shutdown(None),
        ]
    )


def test_shutdown_with_exception_parameter() -> None:
    exception = Exception()
    mock = Mock()
    command = SequenceStartupCommand([mock.command1, mock.command2])
    command.startup()
    command.shutdown(exception)
    mock.assert_has_calls(
        [
            call.command1.startup(),
            call.command2.startup(),
            call.command2.shutdown(exception),
            call.command1.shutdown(exception),
        ]
    )


@pytest.mark.asyncio
async def test_startup_async_and_shutdown_async() -> None:
    mock = AsyncMock()
    command = SequenceStartupCommand([mock.command1, mock.command2])
    await command.startup_async()
    mock.assert_has_calls(
        [
            call.command1.startup_async(),
            call.command2.startup_async(),
        ]
    )
    await command.shutdown_async()
    mock.assert_has_calls(
        [
            call.command1.startup_async(),
            call.command2.startup_async(),
            call.command2.shutdown_async(None),
            call.command1.shutdown_async(None),
        ]
    )


@pytest.mark.asyncio
async def test_startup_async_with_exception() -> None:
    exception = Exception()
    mock = AsyncMock()
    mock.command2.startup_async.side_effect = exception
    command = SequenceStartupCommand([mock.command1, mock.command2])
    with pytest.raises(Exception):
        await command.startup_async()
    mock.assert_has_calls(
        [
            call.command1.startup_async(),
            call.command2.startup_async(),
            call.command1.shutdown_async(exception),
        ]
    )


@pytest.mark.asyncio
async def test_shutdown_async_with_exception() -> None:
    exception = Exception()
    mock = AsyncMock()
    mock.command2.shutdown_async.side_effect = exception
    command = SequenceStartupCommand([mock.command1, mock.command2])
    await command.startup_async()
    with pytest.raises(Exception):
        await command.shutdown_async()
    mock.assert_has_calls(
        [
            call.command1.startup_async(),
            call.command2.startup_async(),
            call.command2.shutdown_async(None),
            call.command1.shutdown_async(None),
        ]
    )


@pytest.mark.asyncio
async def test_shutdown_async_with_exception_parameter() -> None:
    exception = Exception()
    mock = AsyncMock()
    command = SequenceStartupCommand([mock.command1, mock.command2])
    await command.startup_async()
    await command.shutdown_async(exception)
    mock.assert_has_calls(
        [
            call.command1.startup_async(),
            call.command2.startup_async(),
            call.command2.shutdown_async(exception),
            call.command1.shutdown_async(exception),
        ]
    )
