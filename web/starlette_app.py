import uvicorn
import json
from datetime import datetime
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from .data.simple_store import SimpleStore
from .models import Watcher, Process
from .views.render_view import render_view
from .views.render_connected_processes import render_connected_processes
from .views.render_watcher_form import render_watcher_form
from .views.render_watcher import render_watcher


def render_page(title: str, content: str) -> HTMLResponse:
    return HTMLResponse(render_view("page.html", {"title": title, "content": content}))


async def parse_json_request(request: Request) -> dict | None:
    """Attempts to parse JSON from request body. Returns None if parsing fails."""
    try:
        return await request.json()
    except json.JSONDecodeError:
        return None


server = Starlette()
simple_store = SimpleStore()


# -----------------------------------------------------------------------------
# WEB ROUTES
# -----------------------------------------------------------------------------


@server.route("/")
async def homepage_route(request: Request):
    watch_function_form = render_watcher_form()
    process_ids = [process.instance_id for process in simple_store.get_processes()]
    list_container = render_connected_processes(process_ids)
    page_content = watch_function_form + list_container
    return render_page("Home", page_content)


@server.route("/watch-function", methods=["POST"])
async def watch_function_route(request: Request):
    form_data = await request.form()
    function_name = str(form_data.get("function_name"))
    watcher = Watcher(function_name=function_name, status="pending", calls=[])
    simple_store.add_watcher(watcher)
    watcher_view = render_watcher()
    return render_page("Form Response", watcher_view)


# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------


@server.route("/start-connection", methods=["POST"])
async def start_connection_route(request: Request):
    request_data = await parse_json_request(request)
    if request_data is None:
        return JSONResponse("Invalid JSON data\n", status_code=400)

    system_info = request_data.get("system_info")
    if system_info is None:
        return JSONResponse("Invalid request\n", status_code=400)

    instance_id = system_info["process"]["instance_id"]
    new_process = Process(
        instance_id=instance_id,
        connected_at=datetime.now(),
    )
    simple_store.add_process(new_process)
    return JSONResponse("Success\n", status_code=200)


@server.route("/pending-watchers", methods=["GET"])
async def pending_watchers_route(request: Request):
    response: dict[str, list[str]] = {"function_names": []}
    all_watchers = simple_store.get_watchers()
    for watcher in all_watchers:
        if watcher.status == "pending":
            response["function_names"].append(watcher.function_name)

    return JSONResponse(response, status_code=200)


@server.route("/watch-success", methods=["POST"])
async def watch_success_route(request: Request):
    request_data = await parse_json_request(request)
    if request_data is None:
        return JSONResponse("Invalid JSON data\n", status_code=400)

    function_name = request_data.get("function_name")
    if function_name is None:
        return JSONResponse("Invalid request\n", status_code=400)

    watcher = simple_store.get_watcher(function_name)

    watcher.status = "success"
    return JSONResponse("Success\n", status_code=200)



@server.route("/function-call", methods=["POST"])
async def function_call_route(request: Request):
    request_data = await parse_json_request(request)
    if request_data is None:
        return JSONResponse("Invalid JSON data\n", status_code=400)

    function_name = request_data.get("function_name")
    if function_name is None:
        return JSONResponse("Invalid request\n", status_code=400)

    watcher = simple_store.get_watcher(function_name)
    watcher.calls.append(request_data)
    print(f"Received {function_name} call from {watcher.function_name}")
    print(f"Calls: {watcher.calls}")
    return JSONResponse("Success\n", status_code=200)


if __name__ == "__main__":
    uvicorn.run(server, host="127.0.0.1", port=8000)
