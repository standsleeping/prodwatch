from .render_view import render_view

def render_connected_processes(process_ids: list[str]) -> str:
    process_list = [f"<div>{process_id}</div>" for process_id in process_ids]
    process_list_str = "\n".join(process_list)

    list_container = render_view("list-container.html", {"processes": process_list_str})
    return list_container
