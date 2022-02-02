from typing import Optional
from unittest.mock import AsyncMock, Mock, call

import pytest

from galo_startup_commands import ContextManagerStartupCommand


def test_context() -> None:
    class TestCommand(ContextManagerStartupCommand):
        def startup(self) -> None:
            mock.startup()

        def shutdown(self, exception: Optional[BaseException] = None) -> None:
            mock.shutdown(exception)

    mock = Mock()
    with TestCommand():
        mock.assert_has_calls(
            [
                call.startup(),
            ]
        )

    mock.assert_has_calls(
        [
            call.startup(),
            call.shutdown(None),
        ]
    )


def test_context_with_exception() -> None:
    class TestCommand(ContextManagerStartupCommand):
        def startup(self) -> None:
            mock.startup()

        def shutdown(self, exception: Optional[BaseException] = None) -> None:
            mock.shutdown(exception)

    exception = Exception()
    mock = Mock()
    with pytest.raises(Exception):
        with TestCommand():
            raise exception
    mock.assert_has_calls(
        [
            call.startup(),
            call.shutdown(exception),
        ]
    )


@pytest.mark.asyncio
async def test_async_context() -> None:
    class TestCommand(ContextManagerStartupCommand):
        async def startup_async(self) -> None:
            await mock.startup_async()

        async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
            await mock.shutdown_async(exception)

    mock = AsyncMock()
    async with TestCommand():
        mock.assert_has_calls(
            [
                call.startup_async(),
            ]
        )

    mock.assert_has_calls(
        [
            call.startup_async(),
            call.shutdown_async(None),
        ]
    )


@pytest.mark.asyncio
async def test_async_context_with_exception() -> None:
    class TestCommand(ContextManagerStartupCommand):
        async def startup_async(self) -> None:
            await mock.startup_async()

        async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
            await mock.shutdown_async(exception)

    exception = Exception()
    mock = AsyncMock()
    with pytest.raises(Exception):
        async with TestCommand():
            raise exception
    mock.assert_has_calls(
        [
            call.startup_async(),
            call.shutdown_async(exception),
        ]
    )
