import itertools
from collections.abc import Callable, Iterable, Iterator
from typing import cast, overload

from extensionmethods import Extension

from iterable_extensions.types import Grouping, SupportsComparison


class ReusableIterable[TSource, TResult](Iterable[TResult]):
    def __init__(
        self,
        source: Iterable[TSource],
        func: Callable[[Iterable[TSource]], Iterator[TResult]],
    ):
        self._source = source
        self._func = func

    def __iter__(self) -> Iterator[TResult]:
        return self._func(self._source)


class where[TSource](Extension[Iterable[TSource], [], Iterable[TSource]]):
    def __init__(
        self,
        predicate: Callable[[TSource], bool],
    ):
        def _where(source: Iterable[TSource]) -> Iterable[TSource]:
            def _func(source: Iterable[TSource]) -> Iterator[TSource]:
                return (x for x in source if predicate(x))

            return ReusableIterable(source, _func)

        super().__init__(_where)


class select[TSource, TResult](Extension[Iterable[TSource], [], Iterable[TResult]]):
    def __init__(
        self,
        selector: Callable[[TSource], TResult],
    ):
        def _select(source: Iterable[TSource]) -> Iterable[TResult]:
            def _func(source: Iterable[TSource]) -> Iterator[TResult]:
                return map(selector, source)

            return ReusableIterable(source, _func)

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


class order_by[TSource, TKey: SupportsComparison](
    Extension[Iterable[TSource], [], Iterable[TSource]]
):
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
    ):
        def _order_by(source: Iterable[TSource]) -> Iterable[TSource]:
            return sorted(source, key=key_selector)

        super().__init__(_order_by)


class order_by_descending[TSource, TKey: SupportsComparison](
    Extension[Iterable[TSource], [], Iterable[TSource]]
):
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
    ):
        def _order_by(source: Iterable[TSource]) -> Iterable[TSource]:
            return sorted(source, key=key_selector, reverse=True)

        super().__init__(_order_by)


class group_by[TKey: SupportsComparison, TSource](
    Extension[
        Iterable[TSource],
        [],
        Iterable[Grouping[TKey, TSource]],
    ]
):
    def __init__(
        self,
        key_selector: Callable[[TSource], TKey],
    ):
        def _group_by(
            source: Iterable[TSource],
        ) -> Iterable[Grouping[TKey, TSource]]:
            def _func(source: Iterable[TSource]) -> Iterator[Grouping]:
                groups = itertools.groupby(
                    sorted(source, key=key_selector),
                    key=key_selector,
                )

                for key, elements in groups:
                    yield Grouping(key, list(elements))

            return ReusableIterable(source, _func)

        super().__init__(_group_by)
