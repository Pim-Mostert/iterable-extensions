from collections.abc import Callable, Iterable
from typing import cast, overload

from extensionmethods import Extension


class where[TSource](Extension[Iterable[TSource], [], Iterable[TSource]]):
    def __init__(
        self,
        predicate: Callable[[TSource], bool],
    ):
        def _where(source: Iterable[TSource]) -> Iterable[TSource]:
            return filter(predicate, source)

        super().__init__(_where)


class select[TSource, TResult](Extension[Iterable[TSource], [], Iterable[TResult]]):
    def __init__(
        self,
        selector: Callable[[TSource], TResult],
    ):
        def _select(source: Iterable[TSource]) -> Iterable[TResult]:
            return map(selector, source)

        super().__init__(_select)


class to_list[T](Extension[Iterable[T], [], Iterable[T]]):
    def __init__(
        self,
    ):
        super().__init__(list)


class to_dictionary[TSource, TKey, TElement](
    Extension[Iterable[TSource], [], dict[TKey, TElement]]
):
    @overload
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
    ): ...

    @overload
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
        element_selector: Callable[[TSource], TElement],
    ): ...

    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
        element_selector: Callable[[TSource], TElement] | None = None,
    ):
        if element_selector:

            def _to_dictionary(source: Iterable[TSource]) -> dict[TKey, TElement]:
                return {key_selector(x): element_selector(x) for x in source}
        else:

            def _to_dictionary(source: Iterable[TSource]) -> dict[TKey, TElement]:
                return {key_selector(x): cast(TElement, x) for x in source}

        super().__init__(_to_dictionary)


class order_by[TSource, TKey](Extension[Iterable[TSource], [], Iterable[TSource]]):
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
    ):
        def _order_by(source: Iterable[TSource]) -> Iterable[TSource]:
            return sorted(source, key=key_selector)  # pyright: ignore[reportCallIssue, reportArgumentType]

        super().__init__(_order_by)


class order_by_descending[TSource, TKey](
    Extension[Iterable[TSource], [], Iterable[TSource]]
):
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
    ):
        def _order_by(source: Iterable[TSource]) -> Iterable[TSource]:
            return sorted(source, key=key_selector, reverse=True)  # pyright: ignore[reportCallIssue, reportArgumentType]

        super().__init__(_order_by)
