import itertools
from collections.abc import Callable, Iterable, Iterator
from typing import cast, overload

from extensionmethods import Extension

from iterable_extensions.types import Grouping, SupportsComparison


class ReusableIterable[TIn, TOut](Iterable[TOut]):
    def __init__(
        self,
        source: Iterable[TIn],
        func: Callable[[Iterable[TIn]], Iterator[TOut]],
    ):

        self._source = source
        self._func = func

    def __iter__(self) -> Iterator[TOut]:
        return self._func(self._source)


class count[T](Extension[Iterable[T], [], int]):
    def __init__(self):
        """Count the number of elements in an iterable.

        Example:
            ```
            source = [1, 1, 1, 1, 1]

            source | count() # returns 5
            ```
        """

        def _count(source: Iterable[T]) -> int:
            total = 0
            for _ in source:
                total += 1

            return total

        super().__init__(_count)


class group_by[T, TKey: SupportsComparison](
    Extension[
        Iterable[T],
        [Callable[[T], TKey]],
        Iterable[Grouping[TKey, T]],
    ]
):
    def __init__(
        self,
        key_selector: Callable[[T], TKey],
    ):
        """Group the elements in an iterable based on a key.

        Args:
            key_selector (Callable[[T], TKey]): Function to generate the key for each element.

        Example:
            ```
            @dataclass
            class Person:
                age: int
                name: str


            source = [
                Person(10, "Arthur"),
                Person(10, "Becky"),
                Person(20, "Chris"),
                Person(30, "Dave"),
                Person(30, "Eduardo"),
                Person(30, "Felice"),
            ]

            grouped = source | group_by[Person, int](lambda x: x.age)

            print(list(grouped))

            # Returns:
            #
            # [
            #   10: [Person(age=10, name='Arthur'), Person(age=10, name='Becky')],
            #   20: [Person(age=20, name='Chris')],
            #   30: [Person(age=30, name='Dave'), Person(age=30, name='Eduardo'), Person(age=30, name='Felice')]
            # ]
            ```
        """

        def _group_by(
            source: Iterable[T],
            key_selector: Callable[[T], TKey],
        ) -> Iterable[Grouping[TKey, T]]:
            def _func(source: Iterable[T]) -> Iterator[Grouping]:
                groups = itertools.groupby(
                    sorted(source, key=key_selector),
                    key=key_selector,
                )

                for key, elements in groups:
                    yield Grouping(key, list(elements))

            return ReusableIterable(source, _func)

        super().__init__(_group_by, key_selector)


class order_by[T, TKey: SupportsComparison](
    Extension[Iterable[T], [Callable[[T], TKey]], Iterable[T]]
):
    def __init__(
        self,
        key_selector: Callable[[T], TKey],
    ):
        def _order_by(
            source: Iterable[T], key_selector: Callable[[T], TKey]
        ) -> Iterable[T]:
            return sorted(source, key=key_selector)

        super().__init__(_order_by, key_selector)


class order_by_descending[T, TKey: SupportsComparison](
    Extension[Iterable[T], [Callable[[T], TKey]], Iterable[T]]
):
    def __init__(
        self,
        key_selector: Callable[[T], TKey],
    ):
        def _order_by(
            source: Iterable[T], key_selector: Callable[[T], TKey]
        ) -> Iterable[T]:
            return sorted(source, key=key_selector, reverse=True)

        super().__init__(_order_by, key_selector)


class select[TIn, TOut](
    Extension[
        Iterable[TIn],
        [Callable[[TIn], TOut]],
        Iterable[TOut],
    ]
):
    def __init__(
        self,
        selector: Callable[[TIn], TOut],
    ):
        """This is the select class

        Args:
            selector (Callable[[TIn], TOut]): The selector
        """

        def _select(
            source: Iterable[TIn], selector: Callable[[TIn], TOut]
        ) -> Iterable[TOut]:
            def _func(source: Iterable[TIn]) -> Iterator[TOut]:
                return map(selector, source)

            return ReusableIterable(source, _func)

        super().__init__(_select, selector)


class to_dictionary[T, TKey, TValue](
    Extension[
        Iterable[T],
        [Callable[[T], TKey], Callable[[T], TValue] | None],
        dict[TKey, TValue],
    ]
):
    @overload
    def __init__(
        self,
        key_selector: Callable[[T], TKey],
    ): ...

    @overload
    def __init__(
        self,
        key_selector: Callable[[T], TKey],
        value_selector: Callable[[T], TValue],
    ): ...

    def __init__(
        self,
        key_selector: Callable[[T], TKey],
        value_selector: Callable[[T], TValue] | None = None,
    ):
        """to_dictionary main

        Args:
            key_selector (Callable[[TIn], TKey]): _description_
            value_selector (Callable[[TIn], TValue] | None, optional): _description_. Defaults to None.
        """
        if value_selector:

            def _to_dictionary_key_element(
                source: Iterable[T],
                key_selector,
                element_selector,
            ) -> dict[TKey, TValue]:
                return {key_selector(x): element_selector(x) for x in source}

            _to_dictionary = _to_dictionary_key_element
        else:

            def _to_dictionary_key(
                source: Iterable[T],
                key_selector,
                _,
            ) -> dict[TKey, TValue]:

                return {key_selector(x): cast(TValue, x) for x in source}

            _to_dictionary = _to_dictionary_key

        super().__init__(_to_dictionary, key_selector, value_selector)


class to_list[T](Extension[Iterable[T], [], list[T]]):
    def __init__(
        self,
    ):
        super().__init__(list)


class where[T](
    Extension[
        Iterable[T],
        [Callable[[T], bool]],
        Iterable[T],
    ]
):
    def __init__(
        self,
        predicate: Callable[[T], bool],
    ):
        """where

        Args:
            predicate (Callable[[T], bool]): ja mooi

        Example:
            ```
            result = source | where[int](lambda x: x > 2)
            ```
        """

        def _where(source: Iterable[T], predicate: Callable[[T], bool]) -> Iterable[T]:

            def _func(source: Iterable[T]) -> Iterator[T]:
                return (x for x in source if predicate(x))

            return ReusableIterable(source, _func)

        super().__init__(_where, predicate)
