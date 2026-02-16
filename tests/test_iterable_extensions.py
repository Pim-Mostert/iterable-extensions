from iterable_extensions.iterable_extensions import (
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
    assert list(result) == [5, 6, 7, 8]


def test_select():
    # Assign
    source = [1, 2, 3]

    # Act
    result = source | select[int, tuple[int, int]](lambda x: (x, 2 * x))

    # Assert
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
