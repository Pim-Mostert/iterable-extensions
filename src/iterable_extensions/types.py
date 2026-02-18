from collections.abc import Iterable
from typing import Protocol


class SupportsGreaterThan[T](Protocol):
    def __gt__(self, value: int, /) -> bool: ...


class SupportsLessThan[T](Protocol):
    def __lt__(self, value: int, /) -> bool: ...


SupportsComparison = SupportsGreaterThan | SupportsLessThan


class Grouping[TKey, TSource]:
    """A wrapper around an iterable, that also holds its grouping key.

    Args
        key: they key for this group
    """

    def __repr__(self) -> str:
        return f"{self._key}: {self._source}"

    def __init__(self, key: TKey, source: Iterable[TSource]):
        self._key = key
        self._source = source

    @property
    def key(self):
        """Returns the key for this group.

        Returns:
            [TKey]: The key on which this group was based
        """
        return self._key

    def __iter__(self):
        return iter(self._source)
