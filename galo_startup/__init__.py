"""
A library that allows you to flexibly manage the startup and shutdown of an application.
"""

import os
from collections import defaultdict
from importlib import import_module
from inspect import (
    isasyncgenfunction,
    iscoroutinefunction,
    isfunction,
    isgeneratorfunction,
)
from pkgutil import walk_packages
from types import ModuleType, TracebackType
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Collection,
    DefaultDict,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

__all__ = [
    "StartupCommand",
    "FunctionStartupCommand",
    "AsyncFunctionStartupCommand",
    "GeneratorFunctionStartupCommand",
    "AsyncGeneratorFunctionStartupCommand",
    "DependencyGraphNode",
    "DependencyGraphNodeStartupCommand",
    "ContextManagerStartupCommand",
    "SequenceStartupCommand",
    "startup_command",
    "import_module",
    "import_submodules",
    "fetch_startup_commands",
    "to_graph",
    "GraphCycleException",
    "topological_sort",
]


__version__ = "0.1.0"


class StartupCommand:
    def startup(self) -> None:
        raise NotImplementedError()

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        raise NotImplementedError()

    async def startup_async(self) -> None:
        raise NotImplementedError()

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        raise NotImplementedError()


class FunctionStartupCommand(StartupCommand):
    def __init__(self, function: Callable[[], None]) -> None:
        self.__function = function

    def startup(self) -> None:
        self.__function()

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        pass

    async def startup_async(self) -> None:
        self.startup()

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        pass


class AsyncFunctionStartupCommand(StartupCommand):
    def __init__(self, function: Callable[[], Awaitable[None]]) -> None:
        self.__function = function

    def startup(self) -> None:
        raise Exception(
            f"Cannot call an asynchronous function from a synchronous one: "
            f"function={self.__function!r}."
        )

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        pass

    async def startup_async(self) -> None:
        await self.__function()

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        pass


class GeneratorFunctionStartupCommand(StartupCommand):
    def __init__(self, function: Callable[[], Generator[None, None, None]]) -> None:
        self.__function = function
        self.__generator: Optional[Generator[None, None, None]] = None

    def startup(self) -> None:
        if self.__generator is not None:
            return
        generator = self.__function()
        generator.send(None)
        self.__generator = generator

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        if self.__generator is None:
            return
        if exception is None:
            try:
                self.__generator.send(None)
            except StopIteration:
                pass
        else:
            try:
                self.__generator.throw(exception)
            except StopIteration:
                pass

    async def startup_async(self) -> None:
        self.startup()

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        self.shutdown(exception)


class AsyncGeneratorFunctionStartupCommand(StartupCommand):
    def __init__(self, function: Callable[[], AsyncGenerator[None, None]]) -> None:
        self.__function = function
        self.__generator: Optional[AsyncGenerator[None, None]] = None

    def startup(self) -> None:
        raise Exception(
            f"Cannot call an asynchronous generator function from a synchronous one: "
            f"function={self.__function!r}"
        )

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        raise Exception(
            f"Cannot call an asynchronous generator function from a synchronous one: "
            f"function={self.__function!r}"
        )

    async def startup_async(self) -> None:
        if self.__generator is not None:
            return
        generator = self.__function()
        await generator.asend(None)
        self.__generator = generator

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        if self.__generator is None:
            return
        if exception is None:
            try:
                await self.__generator.asend(None)
            except StopAsyncIteration:
                pass
        else:
            try:
                await self.__generator.athrow(exception)
            except StopAsyncIteration:
                pass


class DependencyGraphNode:
    @property
    def name(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    def after(self) -> Optional[Collection[str]]:
        raise NotImplementedError()

    @property
    def before(self) -> Optional[Collection[str]]:
        raise NotImplementedError()

    @property
    def order(self) -> Optional[int]:
        raise NotImplementedError()


class DependencyGraphNodeStartupCommand(DependencyGraphNode, StartupCommand):
    def __init__(
        self,
        command: StartupCommand,
        name: Optional[str] = None,
        after: Optional[Collection[str]] = None,
        before: Optional[Collection[str]] = None,
        order: Optional[int] = None,
    ) -> None:
        self.__command = command
        self.__name = name
        self.__after = after
        self.__before = before
        self.__order = order

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @property
    def after(self) -> Optional[Collection[str]]:
        return self.__after

    @property
    def before(self) -> Optional[Collection[str]]:
        return self.__before

    @property
    def order(self) -> Optional[int]:
        return self.__order

    def startup(self) -> None:
        self.__command.startup()

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        self.__command.shutdown(exception)

    async def startup_async(self) -> None:
        await self.__command.startup_async()

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        await self.__command.shutdown_async(exception)


class ContextManagerStartupCommand(StartupCommand):
    def __enter__(self) -> None:
        self.startup()

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.shutdown(exception)

    async def __aenter__(self) -> None:
        await self.startup_async()

    async def __aexit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.shutdown_async(exception)


class SequenceStartupCommand(ContextManagerStartupCommand):
    def __init__(self, commands: Sequence[StartupCommand]) -> None:
        self.__commands = commands
        self.__started_commands: List[StartupCommand] = []

    def startup(self) -> None:
        for command in self.__commands:
            try:
                command.startup()
            except BaseException as e:
                self.shutdown(e)
                raise e
            else:
                self.__started_commands.append(command)

    def shutdown(self, exception: Optional[BaseException] = None) -> None:
        try:
            command = self.__started_commands.pop()
        except IndexError:
            return
        try:
            command.shutdown(exception)
        finally:
            self.shutdown(exception)

    async def startup_async(self) -> None:
        for command in self.__commands:
            try:
                await command.startup_async()
            except BaseException as e:
                await self.shutdown_async(e)
                raise e
            else:
                self.__started_commands.append(command)

    async def shutdown_async(self, exception: Optional[BaseException] = None) -> None:
        try:
            command = self.__started_commands.pop()
        except IndexError:
            return
        try:
            await command.shutdown_async(exception)
        finally:
            await self.shutdown_async(exception)


C1 = TypeVar("C1", bound=Callable)
C2 = TypeVar("C2", bound=Callable)


def startup_command(
    function: Optional[C1] = None,
    name: Optional[str] = None,
    after: Optional[Collection[str]] = None,
    before: Optional[Collection[str]] = None,
    order: Optional[int] = None,
) -> Union[C1, Callable[[C2], C2]]:
    if function is None:

        def wrapper(function: C2) -> C2:
            return _startup_command(function, name, after, before, order)

        return wrapper
    else:
        return _startup_command(function, name, after, before, order)


def _startup_command(
    function: C1,
    name: Optional[str] = None,
    after: Optional[Collection[str]] = None,
    before: Optional[Collection[str]] = None,
    order: Optional[int] = None,
) -> C1:
    command: StartupCommand
    if isasyncgenfunction(function):
        command = AsyncGeneratorFunctionStartupCommand(function)
    elif iscoroutinefunction(function):
        command = AsyncFunctionStartupCommand(function)
    elif isgeneratorfunction(function):
        command = GeneratorFunctionStartupCommand(function)
    elif isfunction(function):
        command = FunctionStartupCommand(function)
    else:
        raise TypeError("Function expected")

    command = DependencyGraphNodeStartupCommand(command, name, after, before, order)
    setattr(function, "startup_command", command)
    return function


def import_submodules(module: ModuleType) -> Iterable[ModuleType]:
    yield module

    if module.__file__ is None:
        return

    if os.path.basename(module.__file__) != "__init__.py":
        return

    for module_info in walk_packages([os.path.dirname(module.__file__)], f"{module.__name__}."):
        yield import_module(module_info.name)


def fetch_startup_commands(module: ModuleType) -> Iterable[DependencyGraphNodeStartupCommand]:
    for value in vars(module).values():
        if not isfunction(value):
            continue
        try:
            command = getattr(value, "startup_command")
        except AttributeError:
            continue
        if not isinstance(command, DependencyGraphNodeStartupCommand):
            continue
        yield command


T = TypeVar("T")


def pairwise(items: Sequence[T]) -> Iterable[Tuple[T, T]]:
    iter1 = iter(items)
    iter2 = iter(items)
    next(iter2, None)
    return zip(iter1, iter2)


N = TypeVar("N", bound=DependencyGraphNode)


def to_graph(nodes: Iterable[N]) -> Dict[N, Set[N]]:
    graph: Dict[N, Set[N]] = {}
    for node in nodes:
        graph[node] = set()

    name_to_node: Dict[str, N] = {}
    for node in graph.keys():
        name = node.name
        if name is None:
            continue
        name_to_node[name] = node

    for next_node in graph.keys():
        prev_names = next_node.after
        if prev_names is None:
            continue
        for prev_name in prev_names:
            try:
                prev_node = name_to_node[prev_name]
            except KeyError:
                raise Exception(f"Dependency graph node not found: name={prev_name}.") from None
            graph[next_node].add(prev_node)

    for prev_node in graph.keys():
        next_names = prev_node.before
        if next_names is None:
            continue
        for next_name in next_names:
            try:
                next_node = name_to_node[next_name]
            except KeyError:
                raise Exception(f"Dependency graph node not found: name={next_name}.") from None
            graph[next_node].add(prev_node)

    order_to_nodes: DefaultDict[int, Set[N]] = defaultdict(set)
    for node in graph.keys():
        order = node.order
        if order is None:
            continue
        order_to_nodes[order].add(node)

    orders = sorted(order_to_nodes.keys())
    for prev_order, next_order in pairwise(orders):
        for next_node in order_to_nodes[next_order]:
            for prev_node in order_to_nodes[prev_order]:
                graph[next_node].add(prev_node)

    return graph


def get_nodes(graph: Dict[T, Set[T]]) -> Collection[T]:
    nodes: Set[T] = set()
    for k, v in graph.items():
        nodes.add(k)
        for i in v:
            nodes.add(i)
    return nodes


def reverse_graph(graph: Dict[T, Set[T]]) -> Dict[T, Set[T]]:
    reversed_graph: Dict[T, Set[T]] = {node: set() for node in get_nodes(graph)}
    for k, v in graph.items():
        for i in v:
            reversed_graph[i].add(k)
    return reversed_graph


class GraphCycleException(Exception):
    def __init__(self, cycle: Sequence, *args: Any) -> None:
        super().__init__(cycle, *args)

    @property
    def cycle(self) -> Sequence:
        return self.args[0]


def topological_sort(graph: Dict[T, Set[T]]) -> Sequence[T]:
    def helper(node: T) -> Optional[Sequence[T]]:
        if node in visited:
            return None
        if node in current_visited:
            return path[path.index(node) :]
        current_visited.add(node)
        path.append(node)
        parent_nodes = reversed_graph[node]
        for parent_node in parent_nodes:
            cycle = helper(parent_node)
            if cycle:
                return cycle
        visited.add(node)
        current_visited.remove(node)
        path.pop()
        sorted_nodes.append(node)
        return None

    reversed_graph = reverse_graph(graph)
    visited: Set[T] = set()
    current_visited: Set[T] = set()
    path: List[T] = []
    sorted_nodes: List[T] = []
    for node in reversed_graph:
        cycle = helper(node)
        if cycle:
            raise GraphCycleException(cycle[::-1])
    return sorted_nodes[::-1]
