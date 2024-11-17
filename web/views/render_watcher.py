from .render_view import render_view


def render_watcher() -> str:
    return render_view(
        "watcher.html",
        {},
    )
