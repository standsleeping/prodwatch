import uuid
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from .rendering import render_view
from .services.watch_function import watch_function
from .services.rendering.render_connected_processes import render_connected_processes
from .services.rendering.render_function_watch_form import render_function_watch_form
from .inputs import parse_json_request
from .data.simple_store import SimpleStore


def render_page(title: str, content: str) -> HTMLResponse:
    return HTMLResponse(render_view("page.html", {"title": title, "content": content}))


app = Starlette()
simple_store = SimpleStore()


@app.route("/")
async def homepage_route(request: Request):
    watch_function_form = render_function_watch_form()
    list_container = render_connected_processes(simple_store.get_processes())
    page_content = watch_function_form + list_container

    return render_page("Home", page_content)


@app.route("/watch-function", methods=["POST"])
async def watch_function_route(request: Request):
    form_data = await request.form()
    function = str(form_data.get("function"))
    function_id = str(uuid.uuid4())

    watch_function(function)

    page_content = render_view(
        "form-response.html",
        {
            "function_id": function_id,
            "function": function,
        },
    )

    return render_page("Form Response", page_content)


@app.route("/start-connection", methods=["POST"])
async def start_connection_route(request: Request):
    request_data = await parse_json_request(request)
    if request_data is None:
        return HTMLResponse("Invalid JSON data\n", status_code=400)

    system_info = request_data.get("system_info")
    if system_info is None:
        return HTMLResponse("Invalid request\n", status_code=400)

    instance_id = system_info["process"]["instance_id"]
    simple_store.connect_process(instance_id)
    return HTMLResponse("Success\n", status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
