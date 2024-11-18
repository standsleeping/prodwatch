"""
Inspired by the transaction_profiler.py module
in Sentry's Python SDK (https://github.com/getsentry/sentry-python),
which in turn is based on https://github.com/nylas/nylas-perftools.
"""

import os
import sys
import threading
import time
from collections import defaultdict


class SimpleProfiler:
    def __init__(self, frequency=100, function_filter=None):
        self.interval = 1.0 / frequency
        self.active = False
        self.samples = defaultdict(list)  # {thread_id: [stack_traces]}
        self.start_time = None
        self._profiling_thread = None
        self.function_filter = function_filter

    def start(self):
        if self.active:
            return

        self.active = True
        self.start_time = time.time()
        self._profiling_thread = threading.Thread(
            target=self._profile_loop, daemon=True
        )
        self._profiling_thread.start()

    def stop(self):
        if not self.active:
            return

        self.active = False
        if self._profiling_thread:
            self._profiling_thread.join()

    def _profile_loop(self):
        while self.active:
            self._take_sample()
            time.sleep(self.interval)

    def _take_sample(self):
        for thread_id, frame in sys._current_frames().items():
            if thread_id == self._profiling_thread.ident:
                continue  # Skip our profiler thread

            stack = []
            while frame:
                if (
                    self.function_filter
                    and frame.f_code.co_name not in self.function_filter
                ):
                    break

                # Get local variables and arguments
                local_vars = frame.f_locals
                arg_info = {}

                # Get argument information from the code object
                code = frame.f_code
                arg_count = code.co_argcount
                arg_names = code.co_varnames[:arg_count]

                for arg_name in arg_names:
                    if arg_name in local_vars:
                        try:
                            arg_value = repr(local_vars[arg_name])
                            if len(arg_value) > 1000:
                                arg_value = arg_value[:1000] + "..."
                            arg_info[arg_name] = arg_value
                        except Exception:
                            arg_info[arg_name] = "<unprintable>"

                if "args" in local_vars:
                    try:
                        args_value = repr(local_vars["args"])
                        if len(args_value) > 1000:
                            args_value = args_value[:1000] + "..."
                        arg_info["*args"] = args_value
                    except Exception:
                        arg_info["*args"] = "<unprintable>"

                if "kwargs" in local_vars:
                    try:
                        kwargs_value = repr(local_vars["kwargs"])
                        if len(kwargs_value) > 1000:
                            kwargs_value = kwargs_value[:1000] + "..."
                        arg_info["**kwargs"] = kwargs_value
                    except Exception:
                        arg_info["**kwargs"] = "<unprintable>"

                func_name = frame.f_code.co_name
                basename = os.path.basename(frame.f_code.co_filename)

                stack.append(
                    {
                        "filename": frame.f_code.co_filename,
                        "basename": basename,
                        "function": func_name,
                        "lineno": frame.f_lineno,
                        "arguments": arg_info,
                    }
                )
                frame = frame.f_back

            self.samples[thread_id].append(stack)

    def get_stats(self):
        duration = time.time() - self.start_time if self.start_time else 0
        top_functions = self._get_top_functions()
        stats = {
            "duration": duration,
            "top_functions": top_functions,
            "samples_per_thread": {
                thread_id: len(traces) for thread_id, traces in self.samples.items()
            },
        }
        return stats

    def pretty_print_stats(self):
        stats = self.get_stats()
        top_functions = self._pretty_print_top_functions(stats["top_functions"])
        print(f"Duration: {stats['duration']:.4f}s")
        print(f"Samples per thread: {stats['samples_per_thread']}")
        print(f"Top functions:\n{top_functions}")

    def _pretty_print_top_functions(self, top_functions):
        return "\n".join(
            f"  {func['filename']}:{func['function']}, "
            f"count: {func['count']}, "
            f"sample args: {self._get_sample_args(func['filename'], func['function'])}"
            for func in top_functions
        )

    def _get_sample_args(self, filename, function_name):
        """Get a sample of arguments used in calls to this function."""
        for traces in self.samples.values():
            for stack in traces:
                for frame in stack:
                    matches_filename = frame["filename"] == filename
                    matches_basename = frame["basename"] == os.path.basename(filename)
                    if (
                        (matches_filename or matches_basename)
                        and frame["function"] == function_name
                        and frame["arguments"]
                    ):
                        return frame["arguments"]
        return {}

    def _get_top_functions(self):
        function_counts = defaultdict(int)

        for traces in self.samples.values():
            for stack in traces:
                for frame in stack:
                    key = (frame["filename"], frame["function"])
                    function_counts[key] += 1

        # Sort by count and return top 10
        sorted_funcs = sorted(
            function_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return [
            {"filename": fname, "function": func, "count": count}
            for (fname, func), count in sorted_funcs
        ]

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
