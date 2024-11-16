import uuid
import uvicorn
import json
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from .data.simple_store import SimpleStore
from .services.watch_function import watch_function
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


app = Starlette()
simple_store = SimpleStore()


# -----------------------------------------------------------------------------
# WEB ROUTES
# -----------------------------------------------------------------------------


@app.route("/")
async def homepage_route(request: Request):
    watch_function_form = render_watcher_form()
    list_container = render_connected_processes(simple_store.get_processes())
    page_content = watch_function_form + list_container
    return render_page("Home", page_content)


@app.route("/watch-function", methods=["POST"])
async def watch_function_route(request: Request):
    form_data = await request.form()
    function = str(form_data.get("function"))
    function_id = str(uuid.uuid4())
    watch_function(function)
    watch_function_request = render_watcher(function_id, function)
    return render_page("Form Response", watch_function_request)


# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------


@app.route("/start-connection", methods=["POST"])
async def start_connection_route(request: Request):
    request_data = await parse_json_request(request)
    if request_data is None:
        return JSONResponse("Invalid JSON data\n", status_code=400)

    system_info = request_data.get("system_info")
    if system_info is None:
        return JSONResponse("Invalid request\n", status_code=400)

    instance_id = system_info["process"]["instance_id"]
    simple_store.connect_process(instance_id)
    return JSONResponse("Success\n", status_code=200)


@app.route("/pending-watchers", methods=["GET"])
async def pending_watchers_route(request: Request):
    response: dict[str, list[str]] = {"function_names": []}
    return JSONResponse(response, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
