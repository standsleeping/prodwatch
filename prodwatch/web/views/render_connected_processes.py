from .render_view import render_view

def render_connected_processes(processes: list[dict]) -> str:
    process_list = [f"<div>{process['instance_id']}</div>" for process in processes]
    process_list_str = "\n".join(process_list)

    list_container = render_view("list-container.html", {"processes": process_list_str})
    return list_container
