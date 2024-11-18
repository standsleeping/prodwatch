import time
from prodwatch.profiler.simple_profiler import SimpleProfiler


def do_math(total, i):
    total += i * i
    return total


def sample_function():
    total = 0
    for i in range(10000000):
        total = do_math(total, i)
    return total


def example_explicit_kwargs_function(a, b, c=3, d=4):
    time.sleep(0.1)
    return a + b + c + d


if __name__ == "__main__":
    with SimpleProfiler(
        function_filter=["do_math", "example_explicit_kwargs_function"]
    ) as profiler:
        sample_function()
        example_explicit_kwargs_function(1, 2, c=3, d=4)
    profiler.pretty_print_stats()
