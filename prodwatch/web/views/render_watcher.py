from .render_view import render_view


def render_watcher(function_id: str, function: str) -> str:
    return render_view(
        "watcher.html",
        {"function_id": function_id, "function": function},
    )
