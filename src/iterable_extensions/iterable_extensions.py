from collections.abc import Callable, Iterable

from extensionmethods import Extension


class where[T](Extension[Iterable[T], [], Iterable[T]]):
    def __init__(
        self,
        predicate: Callable[[T], bool],
    ):
        def _where(source: Iterable[T]) -> Iterable[T]:
            return filter(predicate, source)

        super().__init__(_where)
