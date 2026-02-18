# iterable-extensions

Collection of useful extension methods to Iterables to enable functional programming. It is heavily inspired by C#'s LINQ.

The extension methods are implemented using [https://pypi.org/project/extensionmethods/](https://pypi.org/project/extensionmethods/). Under the hood they rely strongly on `itertools` and are basically syntactic sugar to write code in a more functional style.

Type-checking is supported, see [Type-checking](#Type-checking).

Important notes:
- Whereas `itertools` generally returns **iterators** that are exhausted after consuming once, `iterable-extensions` generally returns **iterables** that may be consumed repeatedly.
- Similarly to `itertools`, `iterable-extensions` aims to evaluate lazily so that not the entire input iterable is loaded into memory. However, there are some notable exceptions, including:
  - `order_by` and `order_by_descending`
  - `group_by`

**This package is under development. Only a number of extension methods are currently implemented.**

For the full API reference and the currently implemented methods, see [https://iterable-extensions.readthedocs.io/](https://iterable-extensions.readthedocs.io/).

## Example usage

To filter elements in an iterable based on some predicate:
```py
from iterable_extensions import where, to_list

source = [1, 2, 3, 4, 5]

filtered = source | where[int](lambda x: x > 3) # Only numbers greater than 3
lst = filtered | to_list() # Materialize into list

print(lst)
# [4, 5]

lst2 = filtered | to_list() # Iterables can be consumed multiple times
print(lst2)
# [4, 5]

```

To transform elements according to some function:
```py
from iterable_extensions import select, to_list

source = [1, 2, 3, 4, 5]

transformed = source | select[int, str](lambda x: str(2 * x))  # Transform each element
lst = transformed | to_list()  # Materialize into list

print(lst)
# ['2', '4', '6', '8', '10']
```

To group elements based on a key:
```py
from dataclasses import dataclass

from iterable_extensions.iterable_extensions import group_by


@dataclass
class Person:
    age: int
    name: str


source = [
    Person(21, Gender.MALE, "Arthur"),
    Person(37, Gender.FEMALE, "Becky"),
    Person(12, Gender.MALE, "Chris"),
    Person(48, Gender.MALE, "Dave"),
    Person(88, Gender.MALE, "Eduardo"),
    Person(56, Gender.FEMALE, "Felice"),
]

grouped = source | group_by[Person, int](lambda p: p.age) # Group by age
lst = grouped | to_list() # Materialize into list

print(lst)
# [
#   10: [Person(age=10, name='Arthur'), Person(age=10, name='Becky')],
#   20: [Person(age=20, name='Chris')],
#   30: [Person(age=30, name='Dave'), Person(age=30, name='Eduardo'), Person(age=30, name='Felice')]
# ]
```

You can chain these methods into functional-style code. For instance, in the below
example, to get the full name of the oldest male and female:
```py
from dataclasses import dataclass
from enum import IntEnum

from iterable_extensions.iterable_extensions import (
    Grouping,
    first,
    group_by,
    order_by_descending,
    select,
    to_list,
)


class Gender(IntEnum):
    MALE = 1
    FEMALE = 2


@dataclass
class Person:
    age: int
    gender: Gender
    first_name: str
    last_name: str


data = [
    Person(21, Gender.MALE, "Arthur", "Johnson"),
    Person(56, Gender.FEMALE, "Becky", "de Vries"),
    Person(12, Gender.MALE, "Chris", "Lamarck"),
    Person(48, Gender.MALE, "Dave", "Stevens"),
    Person(88, Gender.MALE, "Eduardo", "Doe"),
    Person(37, Gender.FEMALE, "Felice", "van Halen"),
]

grouped = (
    data
    | group_by[Person, Gender](lambda p: p.gender) # Group by gender
    | select[Grouping[Person, Gender], Person]( # Within each group
        lambda g: (
            g 
            # Order by age, descending
            | order_by_descending[Person, int](lambda p: p.age) 
            | first() # Take the first entry
    )
    # For each gender, aggregate first and last name
    | select[Person, str](lambda p: f"{p.first_name} {p.last_name}") 
    | to_list() # Materialize into list
)

print(grouped)
# ['Eduardo Doe', 'Becky de Vries']
```

## Type-checking

The iterable extensions are fully type-annotated and support type inference with
linters as much as possible. However, due to limitations in current type checkers,
inference doesn't propage through the `|` operator. For example:

```py
source: list[int] = [1, 2, 3, 4, 5]

filtered = source | where(lambda x: x > 3)
```

Will give an error like `Operator ">" not supported for types "T@where" and "Literal[3]"` on the lambda body, even though the type of `x` is fully specified through `source`. 

To circumvent this, you can expicitly specify its type: `where[int](lambda x: ...)`. This also gives you autocompletion on `x` in the lambda body.

Alternatively, you can explicitly define the function instead of writing a lambda:
```
def func(x: int) -> bool:
    return x > 3


filtered = source | where(func)
```
Although this hampers the readability of the functional style that the `iterable-extensions` package aims to provide.

Note that the type annotations are only for static checkers. You can ignore these errors and the code will still run fine.


## How to read `Extension[TIn, **P, TOut]`

In the API reference, you'll notice that all extension methods inherit from `Extension[TIn, **P, TOut]`. This class is the core of the `extensionsmethods` package ([https://pypi.org/project/extensionmethods/](https://pypi.org/project/extensionmethods/)). It provides the basic `|`-operator functionality.

The `Extension` class has two type parameters and a paramspec:
- `TIn`: The type that the extension is defined to operate on.
- `**P`: Arbitrary number of arguments that the extension method may take.
- `TOut`: The type of the return value of the extension method.

For example, looking at the signature of `select`:
```
class select[TIn, TOut](
    Extension[
        Iterable[TIn],
        [Callable[[TIn], TOut]],
        Iterable[TOut]
    ]
): ...
```
we see that:
- `TIn` = `Iterable[TIn]`. `select` is defined to operate on iterables of an arbitrary input type.
- `**P` = `[Callable[[TIn], TOut]]`. `select` requires a mapping function as a parameter.
- `TOut` = `Iterable[TOut]`. `select` returns an iterable of an arbitrary output type.

For example:
```py
source: list[int] = [1, 2, 3, 4]

# Allowed. Inputs ints, outputs strings.
source | select[int, str](lambda: str(x)) 

# Not allowed. Expects strings as inputs, but ints are given.
source | select[str, str](lambda: str(x)) 

# Not allowed. Excepts ints as output, but the lambda returns strings.
source | select[int, int](lambda: str(x)) 
```

## Installation

Using pip:
```
pip install iterable-extensions
```

Using uv:
```
uv add iterable-extensions
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
