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


class any[T](Extension[Iterable[T], [Callable[[T], bool] | None], bool]):
    @overload
    def __init__(
        self,
    ): ...

    @overload
    def __init__(
        self,
        predicate: Callable[[T], bool] | None = None,
    ): ...

    def __init__(
        self,
        predicate: Callable[[T], bool] | None = None,
    ):
        """Whether the iterable contains any elements, or whether the iterable contains
        any element that satisfies the predicate.

        Args:
            predicate (Callable[[T], bool] | None, optional): Function to evaluate per element. Defaults to None.

        Example:
            ```
            source = [1, 2, 3]

            result = source | any[int](lambda x: x == 2)

            print(result)
            # True
            ```
        """

        def _any(
            source: Iterable[T],
            predicate: Callable[[T], bool] | None,
        ) -> bool:

            if predicate:
                for value in source:
                    if predicate(value) is True:
                        return True

                return False
            else:
                try:
                    next(iter(source))
                except StopIteration:
                    return False

                return True

        super().__init__(_any, predicate)


class count[T](Extension[Iterable[T], [], int]):
    def __init__(self):
        """Count the number of elements in an iterable.

        Example:
            ```
            source = [1, 1, 1, 1, 1]

            print(source | count())
            # 5
            ```
        """

        def _count(source: Iterable[T]) -> int:
            total = 0
            for _ in source:
                total += 1

            return total

        super().__init__(_count)


class distinct[T](Extension[Iterable[T], [], Iterable[T]]):
    def __init__(self):
        """Returns distinct elements from the iterable.

        Example:
            ```
            source = [1, 3, 4, 1, 3, 7, 9, 3, 7]

            result = source | distinct()

            print(list(result))
            # [1, 3, 4, 7, 9]
            ```
        """

        def _distinct(source: Iterable[T]) -> Iterable[T]:
            def _func(source: Iterable[T]) -> Iterator[T]:
                # unique_everseen - https://docs.python.org/3/library/itertools.html
                seen = set()

                for element in itertools.filterfalse(seen.__contains__, source):
                    seen.add(element)
                    yield element

            return ReusableIterable(source, _func)

        super().__init__(_distinct)


class group_by[T, TKey: SupportsComparison](
    Extension[
        Iterable[T],
        [Callable[[T], TKey]],
        Iterable[Grouping[T, TKey]],
    ]
):
    def __init__(
        self,
        key_selector: Callable[[T], TKey],
    ):
        """Group the elements in an iterable based on a key.

        No prior sorting required.

        Args:
            key_selector (Callable[[T], TKey]): Function to generate the key for each element.

        Note:
            While the returned `Grouping` object itself is an iterable that is evaluated lazily,
            the elements within each individual group are materialized into list when their group
            is iterated. This may lead to memory issues in case of a large number of elements.

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

            grouped = source | group_by[Person, int](lambda p: p.age)

            print(list(grouped))
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
        ) -> Iterable[Grouping[T, TKey]]:
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
        """Order the elements in an iterable based on a key in ascending order.

        Args:
            key_selector (Callable[[T], TKey]): Function to generate the key for each element.

        Note:
            `order_by` materializes the entire input iterable, i.e. does not evaluate lazily.
            This may lead to memory issues in case of large iterables.

        Example:
            ```
            @dataclass
            class Person:
                age: int
                name: str

            source = [
                Person(31, "Arthur"),
                Person(12, "Becky"),
                Person(45, "Chris"),
            ]

            ordered = source | order_by[Person, int](lambda p: p.age)

            print(list(ordered))
            # [
            #     Person(age=12, name='Becky'),
            #     Person(age=31, name='Arthur'),
            #     Person(age=45, name='Chris')
            # ]

            ```
        """

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
        """Order the elements in an iterable based on a key in descending order.

        Args:
            key_selector (Callable[[T], TKey]): Function to generate the key for each element.

        Note:
            `order_by_descending` materializes the entire input iterable, i.e. does not
            evaluate lazily. This may lead to memory issues in case of large iterables.

        Example:
            ```
            @dataclass
            class Person:
                age: int
                name: str

            source = [
                Person(31, "Arthur"),
                Person(12, "Becky"),
                Person(45, "Chris"),
            ]

            ordered = source | order_by_descending[Person, int](lambda p: p.age)

            print(list(ordered))
            # [
            #     Person(age=45, name='Chris')
            #     Person(age=31, name='Arthur'),
            #     Person(age=12, name='Becky'),
            # ]

            ```
        """

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
        """Transform each element in an iterable according to a selector function.

        Args:
            selector (Callable[[TIn], TOut]): Function to transform each element.

        Example:
        ```
            source = [1, 2, 3, 4, 5]

            transformed = source | select[int, str](lambda x: str(2 * x))

            print(list(transformed))
            # ['2', '4', '6', '8', '10']
        ```
        """

        def _select(
            source: Iterable[TIn], selector: Callable[[TIn], TOut]
        ) -> Iterable[TOut]:
            def _func(source: Iterable[TIn]) -> Iterator[TOut]:
                return map(selector, source)

            return ReusableIterable(source, _func)

        super().__init__(_select, selector)


class first[T](Extension[Iterable[T], [], T]):
    def __init__(
        self,
    ):
        """Take the first element of an iterable.

        Raises:
            ValueError: If the iterable contains no elements.

        Example:
            ```
            source = [4, 7, 2]

            result = source | first()

            print(result)
            # 4
            ```
        """

        def _first(source: Iterable[T]) -> T:
            try:
                return next(iter(source))
            except StopIteration:
                raise ValueError("Iterable is empty.")

        super().__init__(_first)


class first_or_none[T](Extension[Iterable[T], [], T | None]):
    def __init__(
        self,
    ):
        """Take the first element of an iterable. Returns None
        if the iterable is empty.

        Examples:
            ```
            source = [4, 7, 2]

            result = source | first_or_none()

            print(result)
            # 4
            ```
        """

        def _first_or_none(source: Iterable[T]) -> T | None:
            try:
                return next(iter(source))
            except StopIteration:
                return None

        super().__init__(_first_or_none)


class last[T](Extension[Iterable[T], [], T]):
    def __init__(
        self,
    ):
        """Find the last element of an iterable.

        Raises:
            ValueError: If the iterable contains no elements.

        Example:
            ```
            source = [4, 7, 2]

            result = source | last()

            print(result)
            # 2
            ```
        """

        def _last(source: Iterable[T]) -> T:
            iterator = iter(source)

            try:
                value = next(iterator)
            except StopIteration:
                raise ValueError("Iterable contains no elements.")

            while True:
                try:
                    value = next(iterator)
                except StopIteration:
                    return value

        super().__init__(_last)


class last_or_none[T](Extension[Iterable[T], [], T | None]):
    def __init__(
        self,
    ):
        """Find the last element of an iterable, or returns None
        if the iterable is empty.

        Example:
            ```
            source = [4, 7, 2]

            result = source | last_or_none()

            print(result)
            # 2
            ```
        """

        def _last_or_none(source: Iterable[T]) -> T | None:
            iterator = iter(source)

            try:
                value = next(iterator)
            except StopIteration:
                return None

            while True:
                try:
                    value = next(iterator)
                except StopIteration:
                    return value

        super().__init__(_last_or_none)


class single[T](Extension[Iterable[T], [], T]):
    def __init__(
        self,
    ):
        """Takes the single element of an iterable.

        Raises:
            ValueError: If the iterable contains no elements, or more than one.

        Example:
            ```
            source = [4]

            result = source | single()

            print(result)
            # 4
            ```
        """

        def _single(source: Iterable[T]) -> T:
            iterator = iter(source)

            try:
                value = next(iterator)

                try:
                    next(iterator)
                except StopIteration:
                    return value
            except StopIteration:
                raise ValueError("Iterable is empty.")

            raise ValueError("Iterable contains more than one element.")

        super().__init__(_single)


class single_or_none[T](Extension[Iterable[T], [], T | None]):
    def __init__(
        self,
    ):
        """Takes the single element of an iterable, or returns None if
        the iterable is empty.

        Raises:
            ValueError: If the iterable contains more than one element.

        Example:
            ```
            source = [4]

            result = source | single_or_none()

            print(result)
            # 4
            ```
        """

        def _single_or_none(source: Iterable[T]) -> T | None:
            iterator = iter(source)

            try:
                value = next(iterator)

                try:
                    next(iterator)
                except StopIteration:
                    return value
            except StopIteration:
                return None

            raise ValueError("Iterable contains more than one element.")

        super().__init__(_single_or_none)


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
        """Transform an iterable into a dictionary based on a key. Optionally transform each element.

        Args:
            key_selector (Callable[[TIn], TKey]): Function to generate key for each element.
            value_selector (Callable[[TIn], TValue] | None, optional): Function to transform each element. Defaults to None.

        Example:
            ```
            @dataclass
            class Person:
                age: int
                name: str


            source = [
                Person(31, "Arthur"),
                Person(12, "Becky"),
                Person(45, "Chris"),
            ]

            dict = source | to_dictionary[Person, int, str](
                lambda p: p.age,
                lambda p: p.name.upper(),
            )

            print(dict)
            # {31: 'ARTHUR', 12: 'BECKY', 45: 'CHRIS'}
            ```
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
        """Materialize an iterable into a list.

        Example:
            ```
            source = range(5)

            lst = source | to_list()

            print(lst)
            # [0, 1, 2, 3, 4]
            ```
        """
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
        """Filter an iterable based on a predicate. Only elements for which the
        predicate evaluates to true are included in the resulting iterable.

        Args:
            predicate (Callable[[T], bool]): Function to include an element.

        Example:
            ```
            source = [1, 2, 3, 4, 5]

            filtered = source | where[int](lambda x: x > 3)

            print(list(filtered))
            # [4, 5]
            ```
        """

        def _where(source: Iterable[T], predicate: Callable[[T], bool]) -> Iterable[T]:

            def _func(source: Iterable[T]) -> Iterator[T]:
                return (x for x in source if predicate(x))

            return ReusableIterable(source, _func)

        super().__init__(_where, predicate)
