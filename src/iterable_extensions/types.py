from collections.abc import Iterable
from typing import Protocol


class SupportsGreaterThan[T](Protocol):
    def __gt__(self, value: int, /) -> bool: ...


class SupportsLessThan[T](Protocol):
    def __lt__(self, value: int, /) -> bool: ...


SupportsComparison = SupportsGreaterThan | SupportsLessThan

