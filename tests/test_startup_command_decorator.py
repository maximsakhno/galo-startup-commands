from unittest.mock import AsyncMock, Mock, call

import pytest

from galo_startup_commands import DependencyGraphNodeStartupCommand, startup_command


def test_without_parameters() -> None:
    @startup_command
    def startup():
        pass

    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    assert command.name is None
    assert command.after is None
    assert command.before is None
    assert command.order is None


def test_with_name_parameter() -> None:
    @startup_command(name="test")
    def startup():
        pass

    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    assert command.name == "test"


def test_with_after_parameter() -> None:
    @startup_command(after=[])
    def startup():
        pass

    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    assert command.after == []


def test_with_before_parameter() -> None:
    @startup_command(before=[])
    def startup():
        pass

    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    assert command.before == []


def test_with_order_parameter() -> None:
    @startup_command(order=0)
    def startup():
        pass

    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    assert command.order == 0


def test_function() -> None:
    @startup_command(order=0)
    def startup():
        mock.startup()

    mock = Mock()
    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    command.startup()
    command.shutdown()
    mock.startup.assert_called_once_with()


def test_generator_function() -> None:
    @startup_command(order=0)
    def startup():
        mock.startup()
        yield
        mock.shutdown()

    mock = Mock()
    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    command.startup()
    mock.assert_has_calls([call.startup()])
    command.shutdown()
    mock.assert_has_calls(
        [
            call.startup(),
            call.shutdown(),
        ]
    )


@pytest.mark.asyncio
async def test_async_function() -> None:
    @startup_command(order=0)
    async def startup():
        await mock.startup_async()

    mock = AsyncMock()
    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    await command.startup_async()
    await command.shutdown_async()
    mock.startup_async.assert_called_once_with()


@pytest.mark.asyncio
async def test_async_generator_function() -> None:
    @startup_command(order=0)
    async def startup():
        await mock.startup_async()
        yield
        await mock.shutdown_async()

    mock = AsyncMock()
    command = getattr(startup, "startup_command")
    assert isinstance(command, DependencyGraphNodeStartupCommand)
    await command.startup_async()
    mock.assert_has_calls([call.startup_async()])
    await command.shutdown_async()
    mock.assert_has_calls(
        [
            call.startup_async(),
            call.shutdown_async(),
        ]
    )


def test_not_a_function() -> None:
    with pytest.raises(TypeError):
        startup_command(Mock())
