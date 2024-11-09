import time
from prodwatch.profiling.simple_profiler import SimpleProfiler


def test_init():
    profiler = SimpleProfiler(frequency=100)
    assert profiler.interval == 0.01
    assert not profiler.active
    assert profiler.start_time is None
    assert profiler._profiling_thread is None


def test_start_stop():
    profiler = SimpleProfiler()
    profiler.start()
    assert profiler.active
    assert profiler.start_time is not None
    assert profiler._profiling_thread is not None
    assert profiler._profiling_thread.is_alive()

    profiler.stop()
    assert not profiler.active
    assert not profiler._profiling_thread.is_alive()


def test_context_manager():
    with SimpleProfiler() as profiler:
        assert profiler.active
        time.sleep(0.1)

    assert not profiler.active
    assert len(profiler.samples) > 0


def test_example_func_filter():
    def target_function():
        time.sleep(0.1)

    with SimpleProfiler(function_filter=["target_function"]) as profiler:
        target_function()

    stats = profiler.get_stats()
    top_functions = stats["top_functions"]

    function_names = [func["function"] for func in top_functions]
    assert "target_function" in function_names


def test_stats():
    with SimpleProfiler() as profiler:
        time.sleep(0.1)

    stats = profiler.get_stats()

    assert "duration" in stats
    assert "top_functions" in stats
    assert "samples_per_thread" in stats
    assert isinstance(stats["duration"], float)
    assert isinstance(stats["top_functions"], list)
    assert isinstance(stats["samples_per_thread"], dict)


def test_multiple_start_stops():
    profiler = SimpleProfiler()

    profiler.start()
    time.sleep(0.1)
    profiler.stop()

    profiler.start()
    time.sleep(0.1)
    profiler.stop()

    assert not profiler.active
    assert len(profiler.samples) > 0


def example_func(x, y):
    time.sleep(0.1)  # Ensure we get at least one sample
    return x + y


def example_args_function(x, y, *args):
    time.sleep(0.1)
    return x + y + sum(args)


def example_kwargs_function(x, y, **kwargs):
    time.sleep(0.1)
    return x + y + sum(kwargs.values())


def example_all_args_function(x, y, *args, **kwargs):
    time.sleep(0.1)
    return x + y + sum(args) + sum(kwargs.values())


def example_explicit_kwargs_function(a, b, c=3, d=4):
    time.sleep(0.1)
    return a + b + c + d


def test_argument_capture():
    # Test regular arguments
    with SimpleProfiler(frequency=100, function_filter=["example_func"]) as profiler:
        example_func(10, 20)

    args = profiler._get_sample_args("test_simple_profiler.py", "example_func")
    assert "x" in args
    assert "y" in args
    assert args["x"] == "10"
    assert args["y"] == "20"


def test_varargs_capture():
    # Test *args capture
    with SimpleProfiler(
        frequency=100, function_filter=["example_args_function"]
    ) as profiler:
        example_args_function(10, 20, 30, 40, 50)

    args = profiler._get_sample_args("test_simple_profiler.py", "example_args_function")
    assert "x" in args
    assert "y" in args
    assert "*args" in args
    assert args["x"] == "10"
    assert args["y"] == "20"
    assert "(30, 40, 50)" in args["*args"]


def test_kwargs_capture():
    # Test **kwargs capture
    with SimpleProfiler(
        frequency=100, function_filter=["example_kwargs_function"]
    ) as profiler:
        example_kwargs_function(10, 20, a=30, b=40)

    args = profiler._get_sample_args(
        "test_simple_profiler.py", "example_kwargs_function"
    )
    assert "x" in args
    assert "y" in args
    assert "**kwargs" in args
    assert args["x"] == "10"
    assert args["y"] == "20"
    assert "'a': 30" in args["**kwargs"]
    assert "'b': 40" in args["**kwargs"]


def test_all_args_capture():
    # Test combination of regular args, *args, and **kwargs
    with SimpleProfiler(
        frequency=100, function_filter=["example_all_args_function"]
    ) as profiler:
        example_all_args_function(10, 20, 30, 40, a=50, b=60)

    args = profiler._get_sample_args(
        "test_simple_profiler.py", "example_all_args_function"
    )
    assert "x" in args
    assert "y" in args
    assert "*args" in args
    assert "**kwargs" in args
    assert args["x"] == "10"
    assert args["y"] == "20"
    assert "(30, 40)" in args["*args"]
    assert "'a': 50" in args["**kwargs"]
    assert "'b': 60" in args["**kwargs"]


def test_explicit_kwargs():
    with SimpleProfiler(
        frequency=100, function_filter=["example_explicit_kwargs_function"]
    ) as profiler:
        example_explicit_kwargs_function(10, 20, c=30, d=40)

    args = profiler._get_sample_args(
        "test_simple_profiler.py", "example_explicit_kwargs_function"
    )
    assert "a" in args
    assert "b" in args
    assert "c" in args
    assert "d" in args
    assert args["c"] == "30"
    assert args["d"] == "40"


def test_long_argument_truncation():
    long_string = "a" * 2000
    with SimpleProfiler(frequency=100, function_filter=["example_func"]) as profiler:
        example_func(long_string, "20")

    args = profiler._get_sample_args("test_simple_profiler.py", "example_func")
    assert len(args["x"]) <= 1003  # 1000 chars + "..."
    assert args["x"].endswith("...")


def example_func_with_unprintable_arg(x):
    time.sleep(0.1)
    return x


def test_unprintable_argument():
    class UnprintableObject:
        def __repr__(self):
            raise Exception("Cannot print this object")

    with SimpleProfiler(
        frequency=100, function_filter=["example_func_with_unprintable_arg"]
    ) as profiler:
        example_func_with_unprintable_arg(UnprintableObject())

    args = profiler._get_sample_args(
        "test_simple_profiler.py", "example_func_with_unprintable_arg"
    )
    assert args["x"] == "<unprintable>"
