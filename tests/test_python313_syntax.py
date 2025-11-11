"""Test parsing of Python 3.10-3.13 syntax features"""

import pytest
from pylext.core.parse import ParseContext, parse


def parse_code(code):
    """Helper function to test if code can be parsed without errors"""
    with ParseContext({}) as px:
        list(parse(code, px))


def test_simple_existing_syntax():
    """Baseline test - simple existing Python syntax"""
    parse_code("""
x = 1 + 2
def foo():
    return 42
""")


def test_pattern_matching_literals():
    """Python 3.10: Pattern matching with literals and or-pattern"""
    parse_code("""
match x:
    case 0:
        y = "zero"
    case 1 | 2:
        y = "one or two"
    case _:
        y = "other"
""")


def test_pattern_matching_guard():
    """Python 3.10: Pattern matching with guard"""
    parse_code("""
match value:
    case x if x > 0:
        result = "positive"
""")


def test_pattern_matching_sequences():
    """Python 3.10: Pattern matching with sequence patterns"""
    parse_code("""
match point:
    case [0, 0]:
        result = "origin"
    case [x, y]:
        result = f"({x}, {y})"
""")


def test_pattern_matching_mappings():
    """Python 3.10: Pattern matching with mapping patterns"""
    parse_code("""
match data:
    case {"name": n, "age": a}:
        result = f"{n}: {a}"
""")


def test_pattern_matching_class():
    """Python 3.10: Pattern matching with class patterns"""
    parse_code("""
match obj:
    case Point(x=0, y=0):
        result = "origin"
    case Point(x=px, y=py):
        result = f"point at {px}, {py}"
""")


def test_pattern_matching_star():
    """Python 3.10: Pattern matching with star patterns"""
    parse_code("""
match command:
    case ["go", direction]:
        move(direction)
    case ["take", *items]:
        inventory.extend(items)
    case ["drop", item, *rest]:
        drop(item)
""")


def test_union_types():
    """Python 3.10: Union types with | operator"""
    parse_code("""
def func(x: int | str) -> int | None:
    return x if isinstance(x, int) else None
""")


def test_parenthesized_context_managers():
    """Python 3.10: Parenthesized context managers"""
    parse_code("""
with (
    open('file1.txt') as f1,
    open('file2.txt') as f2
):
    data = f1.read()
""")


def test_exception_groups():
    """Python 3.11: Exception groups with except*"""
    parse_code("""
try:
    raise ExceptionGroup("errors", [ValueError(), TypeError()])
except* ValueError as e:
    print("ValueError")
except* TypeError as e:
    print("TypeError")
""")


def test_type_parameters_function():
    """Python 3.12: Type parameters for functions"""
    parse_code("""
def identity[T](x: T) -> T:
    return x
""")


def test_type_parameters_class():
    """Python 3.12: Type parameters for classes"""
    parse_code("""
class Container[T]:
    def __init__(self, value: T):
        self.value = value
""")


def test_type_statement():
    """Python 3.12: Type statement"""
    parse_code("""
type Point = tuple[float, float]
type IntOrStr = int | str
""")


def test_type_parameters_with_bounds():
    """Python 3.12: Type parameters with bounds"""
    parse_code("""
def process[T: int | str](value: T) -> T:
    return value
""")


def test_complex_type_params():
    """Python 3.12: Complex type parameters"""
    parse_code("""
class MyClass[T, U: int, *Args, **KWArgs]:
    def method[V](self, x: V) -> V:
        return x
""")


def test_combined_features():
    """Test combining multiple new features"""
    parse_code("""
def process[T](value: int | str) -> T | None:
    match value:
        case int(x) if x > 0:
            return x
        case str(s):
            return s
        case _:
            return None

type Result[T] = T | None

with (
    open('input.txt') as f1,
    open('output.txt') as f2
):
    data = f1.read()
    f2.write(data)
""")
