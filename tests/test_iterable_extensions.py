from iterable_extensions.iterable_extensions import (
    count,
    group_by,
    order_by,
    order_by_descending,
    select,
    to_dictionary,
    to_list,
    where,
)


def test_where():
    # Assign
    source = [1, 2, 3, 4, 5, 6, 7, 8]

    # Act
    result = source | where[int](lambda x: x > 4)

    # Assert
    for _ in range(2):  # Test reusable iterable
        assert list(result) == [5, 6, 7, 8]


def test_select():
    # Assign
    source = [1, 2, 3]

    # Act
    result = source | select[int, tuple[int, int]](lambda x: (x, 2 * x))

    # Assert
    for _ in range(2):  # Test reusable iterable
        assert list(result) == [(1, 2), (2, 4), (3, 6)]


def test_to_list():
    # Assign
    source = (x for x in [1, 2, 3])

    # Act
    result = source | to_list[int]()

    # Assert
    assert type(result) is list
    assert result == [1, 2, 3]


def test_to_dictionary_key():
    # Assign
    source = [1, 2, 3]

    # Act
    result = source | to_dictionary[int, int, int](
        lambda x: 2 * x,
    )

    # Assert
    assert type(result) is dict
    assert len(result) == 3

    for x in source:
        assert result[2 * x] == x


def test_to_dictionary_key_and_element():
    # Assign
    source = [1, 2, 3]

    # Act
    result = source | to_dictionary[int, int, str](
        lambda x: 2 * x,
        lambda x: str(x),
    )

    # Assert
    assert type(result) is dict
    assert len(result) == 3

    for x in source:
        assert result[2 * x] == str(x)


def test_order_by():
    # Assign
    source = [3, 5, 1, 2, 4]

    # Act
    result = source | order_by[int, int](lambda x: x)

    # Assert
    for _ in range(2):  # Test reusable iterable
        assert list(result) == [1, 2, 3, 4, 5]


def test_order_by_descending():
    # Assign
    source = [3, 5, 1, 2, 4]

    # Act
    result = source | order_by_descending[int, int](lambda x: x)

    # Assert
    for _ in range(2):  # Test reusable iterable
        assert list(result) == [5, 4, 3, 2, 1]


def test_group_by():
    class Person:
        def __init__(self, age: int, name: str):
            self.age = age
            self.name = name

    # Assign
    source = [
        Person(10, "Arthur"),
        Person(10, "Becky"),
        Person(20, "Chris"),
        Person(30, "Dave"),
        Person(30, "Eduardo"),
        Person(30, "Felice"),
    ]

    # Act
    groups = source | group_by[int, Person](lambda p: p.age)

    # Assert
    for _ in range(2):  # Test reusable iterable
        groups_list = list(groups)
        assert len(groups_list) == 3

        for _ in range(2):  # Test reusable iterable
            g0 = list(groups_list[0])
            assert len(g0) == 2
            assert [p.name for p in g0] == ["Arthur", "Becky"]

            g1 = list(groups_list[1])
            assert len(g1) == 1
            assert [p.name for p in g1] == ["Chris"]

            g2 = list(groups_list[2])
            assert len(g2) == 3
            assert [p.name for p in g2] == ["Dave", "Eduardo", "Felice"]


def test_count():
    # Assign
    source = [1, 2, 3, 4, 5, 6, 7, 8]

    # Act
    result = source | count[int]()

    # Assert
    assert result == len(source)
