def format_function_call(
    function_name: str, args: list, kwargs: dict, execution_time_ms: float
) -> str:
    args_str = ", ".join(str(arg) for arg in args)
    kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    params = f"{args_str}"
    if kwargs_str:
        params += f", {kwargs_str}" if args_str else kwargs_str

    return f"<div style='font-family: monospace;'>{function_name}({params}) {execution_time_ms}ms</div>"


def function_calls(function_name: str, calls: list[dict]) -> str:
    call_divs = []
    for call in calls:
        args = call.get("args", [])
        kwargs = call.get("kwargs", {})
        execution_time_ms = int(call.get("execution_time_ms", 0))
        call_div = format_function_call(function_name, args, kwargs, execution_time_ms)
        call_divs.append(call_div)

    call_divs_str = "".join(call_divs)
    return f"<div style='font-family: monospace;'>{call_divs_str}</div>"
