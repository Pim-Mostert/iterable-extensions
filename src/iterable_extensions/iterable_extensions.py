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


class select[TIn, TOut](Extension[Iterable[TIn], [], Iterable[TOut]]):
    def __init__(
        self,
        func: Callable[[TIn], TOut],
    ):
        def _select(source: Iterable[TIn]) -> Iterable[TOut]:
            return map(func, source)

        super().__init__(_select)


class to_list[T](Extension[Iterable[T], [], Iterable[T]]):
    def __init__(
        self,
    ):
        super().__init__(list)
