from .render_view import render_view


def render_function_watch_request(function_id: str, function: str) -> str:
    return render_view(
        "function-watch-request.html",
        {"function_id": function_id, "function": function},
    )
