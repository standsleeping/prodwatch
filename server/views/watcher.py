from .render_html import render_html


def watcher(watcher_id: str) -> str:
    watcher_conatiner = render_html("watcher.html", {"watcher_id": watcher_id})
    return watcher_conatiner
