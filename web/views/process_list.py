from .render_html import render_html

def process_list(process_ids: list[str]) -> str:
    process_list = [f"<div>{process_id}</div>" for process_id in process_ids]
    process_list_str = "\n".join(process_list)

    list_container = render_html("process-list.html", {"processes": process_list_str})
    return list_container
