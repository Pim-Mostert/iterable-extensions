from collections.abc import Iterable
from typing import Protocol


class SupportsGreaterThan[T](Protocol):
    def __gt__(self, value: int, /) -> bool: ...


class SupportsLessThan[T](Protocol):
    def __lt__(self, value: int, /) -> bool: ...


SupportsComparison = SupportsGreaterThan | SupportsLessThan


class Grouping[TKey, TSource]:
    def __repr__(self) -> str:
        return f"{self._key}: {self._source}"

    def __init__(self, key: TKey, source: Iterable[TSource]):
        self._key = key
        self._source = source

    @property
    def key(self):
        return self._key

    def __iter__(self):
        return iter(self._source)
