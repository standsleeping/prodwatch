from server.views.function_calls import format_function_call, function_calls


def test_format_function_call_basic():
    """Test basic function call formatting with just args."""
    html = format_function_call("test_func", [1, 2], {}, 50)
    assert html == "<div style='font-family: monospace;'>test_func(1, 2) 50ms</div>"


def test_format_function_call_kwargs():
    """Test function call formatting with kwargs only."""
    html = format_function_call("test_func", [], {"a": 1, "b": 2}, 50)
    assert html == "<div style='font-family: monospace;'>test_func(a=1, b=2) 50ms</div>"


def test_format_function_call_mixed():
    """Test function call formatting with both args and kwargs."""
    html = format_function_call("test_func", [1, 2], {"c": 3}, 50)
    assert html == "<div style='font-family: monospace;'>test_func(1, 2, c=3) 50ms</div>"


def test_format_function_call_empty():
    """Test function call formatting with no parameters."""
    html = format_function_call("test_func", [], {}, 50)
    assert html == "<div style='font-family: monospace;'>test_func() 50ms</div>"


def test_function_calls_empty():
    """Test function calls view with no calls."""
    html = function_calls("test_func", [])
    assert html == "<div style='font-family: monospace;'></div>"


def test_function_calls_single():
    """Test function calls view with a single call."""
    calls = [{"args": [1, 2], "kwargs": {"c": 3}}]
    html = function_calls("test_func", calls)
    assert html == "<div style='font-family: monospace;'><div style='font-family: monospace;'>test_func(1, 2, c=3) 0ms</div></div>"


def test_function_calls_multiple():
    """Test function calls view with multiple calls."""
    calls = [
        {"args": [1, 2], "kwargs": {}},
        {"args": [], "kwargs": {"a": 3}},
    ]
    expected = (
        "<div style='font-family: monospace;'>test_func(1, 2) 0ms</div>"
        "<div style='font-family: monospace;'>test_func(a=3) 0ms</div>"
    )
    html = function_calls("test_func", calls)
    assert html == f"<div style='font-family: monospace;'>{expected}</div>"


def test_function_calls_missing_args_kwargs():
    """Test function calls view with missing args/kwargs in call data."""
    calls = [
        {"args": [1, 2]},  # missing kwargs
        {"kwargs": {"a": 3}},  # missing args
        {},  # missing both
    ]
    expected = (
        "<div style='font-family: monospace;'>test_func(1, 2) 0ms</div>"
        "<div style='font-family: monospace;'>test_func(a=3) 0ms</div>"
        "<div style='font-family: monospace;'>test_func() 0ms</div>"
    )
    html = function_calls("test_func", calls)
    assert html == f"<div style='font-family: monospace;'>{expected}</div>"