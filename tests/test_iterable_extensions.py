from iterable_extensions.iterable_extensions import select, to_list, where


def test_where():
    # Assign
    source = [1, 2, 3, 4, 5, 6, 7, 8]

    # Act
    result = source | where[int](lambda x: x > 4)

    # Assert
    assert list(result) == [5, 6, 7, 8]
