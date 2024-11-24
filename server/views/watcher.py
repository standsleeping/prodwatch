from .render_html import render_html


def watcher(function_name: str) -> str:
    watcher_conatiner = render_html("watcher.html", {"function_name": function_name})
    return watcher_conatiner
