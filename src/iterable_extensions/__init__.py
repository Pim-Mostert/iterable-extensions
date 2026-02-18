from importlib.metadata import PackageNotFoundError, version

from .iterable_extensions import (
    count,
    first,
    first_or_none,
    group_by,
    order_by,
    order_by_descending,
    select,
    single,
    single_or_none,
    to_dictionary,
    to_list,
    where,
)

try:
    __version__ = version("iterable_extensions")
except PackageNotFoundError:
    __version__ = "noinstall"

__all__ = [
    "count",
    "first",
    "first_or_none",
    "group_by",
    "order_by",
    "order_by_descending",
    "select",
    "single",
    "single_or_none",
    "to_dictionary",
    "to_list",
    "where",
]
