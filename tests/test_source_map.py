"""Tests for source map generation"""

import pytest
from pylext.base import exec_macros


def test_simple_source_map():
    """Test that source map is generated for simple code"""
    code = """
x = 1
y = 2
z = x + y
"""
    vars = {}
    exec_macros(code.strip(), vars, filename="test.pyg")

    # Check that source map exists
    assert '__pylext_source_map__' in vars
    source_map = vars['__pylext_source_map__']

    # Check source map structure
    assert source_map['version'] == 1
    assert source_map['source_file'] == 'test.pyg'
    assert 'mappings' in source_map
    assert len(source_map['mappings']) > 0

    # Check that mappings have correct format
    for mapping in source_map['mappings']:
        assert len(mapping) == 4  # [pyg_line, pyg_col, py_line, py_col]
        assert all(isinstance(x, int) for x in mapping)
        assert all(x >= 0 for x in mapping)


def test_macro_source_map():
    """Test source map with macro expansion"""
    code = """
gimport pylext.macros.operator

defmacro guard(stmt, 'guard', cond: test, EOL):
    return stmt`if not (${cond}): return False\\n`

def check_positive(x):
    guard x > 0
    return True
"""
    vars = {}
    exec_macros(code.strip(), vars, filename="test_macro.pyg")

    # Check that source map exists
    assert '__pylext_source_map__' in vars
    source_map = vars['__pylext_source_map__']

    # Source map should have mappings
    assert len(source_map['mappings']) > 0

    # Find mappings for the guard macro line (should map back to original)
    # The guard statement is on line 7 in the original
    guard_mappings = [m for m in source_map['mappings'] if m[0] == 7]
    assert len(guard_mappings) > 0, "Should have mappings for guard statement"


def test_source_map_line_tracking():
    """Test that line numbers are tracked correctly"""
    code = """x = 1
y = 2
z = 3"""
    vars = {}
    exec_macros(code, vars, filename="test_lines.pyg")

    source_map = vars['__pylext_source_map__']

    # Should have at least one mapping per line
    pyg_lines = set(m[0] for m in source_map['mappings'])
    assert 1 in pyg_lines or 2 in pyg_lines or 3 in pyg_lines

    # Python lines should also be reasonable
    py_lines = set(m[2] for m in source_map['mappings'])
    assert len(py_lines) > 0
    assert max(py_lines) <= 10  # Shouldn't generate too many lines for simple code


def test_multiline_statement_source_map():
    """Test source map for multiline statements"""
    code = """
def foo(x,
        y,
        z):
    return x + y + z
"""
    vars = {}
    exec_macros(code.strip(), vars, filename="test_multiline.pyg")

    source_map = vars['__pylext_source_map__']
    assert len(source_map['mappings']) > 0

    # Should have mappings from multiple lines of the function definition
    pyg_lines = set(m[0] for m in source_map['mappings'])
    assert len(pyg_lines) > 1, "Should track multiple lines for multiline statement"


def test_source_map_position_lookup():
    """Test that we can look up original positions"""
    code = """x = 1
y = 2
z = x + y"""
    vars = {}
    exec_macros(code, vars, filename="test_lookup.pyg")

    source_map = vars['__pylext_source_map__']

    # Helper function to find original position
    def find_original_position(py_line, py_col):
        best = None
        best_distance = float('inf')

        for mapping in source_map['mappings']:
            pyg_line, pyg_col, mapped_py_line, mapped_py_col = mapping
            if mapped_py_line == py_line:
                distance = abs(mapped_py_col - py_col)
                if distance < best_distance:
                    best_distance = distance
                    best = (pyg_line, pyg_col)

        return best

    # Try to find position for line 1
    result = find_original_position(1, 0)
    assert result is not None, "Should find mapping for line 1"
    assert result[0] >= 1, "Should map to a valid line in original"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
