from unittest.mock import Mock, call

import pytest

from galo_startup_commands import GeneratorFunctionStartupCommand


def test_startup_and_shutdown() -> None:
    def function():
        mock.startup()
        yield
        mock.shutdown()

    mock = Mock()
    command = GeneratorFunctionStartupCommand(function)

    command.startup()
    mock.assert_has_calls(
        [
            call.startup(),
        ]
    )

    command.shutdown()
    mock.assert_has_calls(
        [
            call.startup(),
            call.shutdown(),
        ]
    )


def test_startup_twice() -> None:
    def function():
        mock.startup()
        yield

    mock = Mock()
    command = GeneratorFunctionStartupCommand(function)
    command.startup()
    command.startup()
    mock.startup.assert_called_once_with()


def test_shutdown_before_startup() -> None:
    def function():
        mock.startup()
        yield
        mock.shutdown()

    mock = Mock()
    command = GeneratorFunctionStartupCommand(function)
    command.shutdown()
    mock.startup.assert_not_called()
    mock.shutdown.assert_not_called()


def test_shutdown_with_exception() -> None:
    def function():
        try:
            yield
        except Exception as e:
            mock.shutdown(e)

    exception = Exception()
    mock = Mock()
    command = GeneratorFunctionStartupCommand(function)
    command.startup()
    command.shutdown(exception)
    mock.shutdown.assert_called_once_with(exception)


@pytest.mark.asyncio
async def test_startup_async_and_shutdown_async() -> None:
    def function():
        mock.startup()
        yield
        mock.shutdown()

    mock = Mock()
    command = GeneratorFunctionStartupCommand(function)

    await command.startup_async()
    mock.assert_has_calls(
        [
            call.startup(),
        ]
    )

    await command.shutdown_async()
    mock.assert_has_calls(
        [
            call.startup(),
            call.shutdown(),
        ]
    )
