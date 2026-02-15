from importlib.metadata import PackageNotFoundError, version

from .iterable_extensions import where

try:
    __version__ = version("iterable_extensions")
except PackageNotFoundError:
    __version__ = "noinstall"

__all__ = [
    "where",
]
