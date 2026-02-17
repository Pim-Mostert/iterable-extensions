from importlib.metadata import PackageNotFoundError, version

from .iterable_extensions import (
    count,
    group_by,
    order_by,
    order_by_descending,
    select,
    to_dictionary,
    to_list,
    where,
)

try:
    __version__ = version("iterable_extensions")
except PackageNotFoundError:
    __version__ = "noinstall"

__all__ = [
    "where",
    "select",
    "to_list",
    "to_dictionary",
    "order_by",
    "order_by_descending",
    "group_by",
    "count",
]
