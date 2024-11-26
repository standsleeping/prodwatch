import uvicorn
from typing import TypeVar, Callable, Any, TypeAlias, Awaitable
from pydantic import BaseModel, Field, ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, StreamingResponse
from app import ProdwatchApp
from .views.render_html import render_html
from .views.process_list import process_list
from .views.add_watcher_form import add_watcher_form
from .views.watcher import watcher
from .views.function_calls import function_calls


class ProcessInfo(BaseModel):
    instance_id: str


class SystemInfo(BaseModel):
    process: ProcessInfo


class AddProcessEvent(BaseModel):
    system_info: SystemInfo


class ConfirmWatcherEvent(BaseModel):
    function_name: str


class LogFunctionCall(BaseModel):
    function_name: str
    args: list = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)


T = TypeVar("T", bound=BaseModel)
RouteHandler_T: TypeAlias = Callable[[Request, T], Awaitable[Any]]
ValidatedRouteHandler_T: TypeAlias = Callable[[Request], Awaitable[Any]]


def render_page(title: str, content: str) -> HTMLResponse:
    return HTMLResponse(render_html("page.html", {"title": title, "content": content}))


def json_response(message: str = "Success", status_code: int = 200) -> JSONResponse:
    return JSONResponse(message + "\n", status_code=status_code)


async def validate_request_model(
    request: Request, model_class: type[T]
) -> tuple[T | None, dict[str, str] | None]:
    """Validates request data against a Pydantic model"""
    try:
        data = await request.json()
        request_data = model_class.model_validate(data)
        return request_data, None
    except ValidationError as e:
        error_data = {"error": "Invalid request data", "details": str(e)}
        return None, error_data


server = Starlette()
app = ProdwatchApp()


@server.route("/", methods=["GET"])
async def root(request: Request):
    form_html = add_watcher_form()
    process_ids = app.get_process_ids()
    list_container = process_list(process_ids)
    return render_page("Home", form_html + list_container)


@server.route("/pending-function-names", methods=["GET"])
async def pending_function_names(request: Request):
    pending_function_names = app.get_pending_function_names()
    response = {"function_names": list(pending_function_names)}
    return JSONResponse(response, status_code=200)


@server.route("/watcher-stream", methods=["GET"])
async def watcher_stream(request: Request):
    function_name = request.query_params.get("function_name", "unknown")
    max_events = int(request.query_params.get("max_events", 1000))

    return StreamingResponse(
        event_stream(function_name, max_events), media_type="text/event-stream"
    )


async def event_stream(function_name: str, max_events: int):
    event_count = 0
    queue = app.function_queues[function_name]

    while True:
        function_name = await queue.get()

        calls = app.get_function_calls(function_name)

        html = function_calls(function_name, calls)
        if html:
            data = f"event: SomeEventName\ndata: {html}\n\n"
            yield data

        event_count += 1
        if max_events and event_count >= max_events:
            yield "event: StreamClosing\ndata: N/A\n\n"
            break


@server.route("/add-watcher", methods=["POST"])
async def add_watcher(request: Request):
    form_data = await request.form()
    function_name = str(form_data.get("function_name"))
    app.add_watcher(function_name)
    return render_page("Watcher", watcher(function_name))


@server.route("/events", methods=["POST"])
async def events(request: Request):
    try:
        data = await request.json()
        event_name = data.get("event_name")
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    if not event_name:
        return JSONResponse({"error": "Missing event_name"}, status_code=400)

    if event_name == "add-process":
        add_process_request_data, error_data = await validate_request_model(
            request, AddProcessEvent
        )
        if error_data is not None:
            return JSONResponse(error_data, status_code=400)
        assert add_process_request_data is not None
        instance_id = add_process_request_data.system_info.process.instance_id
        app.add_process(instance_id)
        return json_response()

    elif event_name == "confirm-watcher":
        confirm_watcher_request_data, error_data = await validate_request_model(
            request, ConfirmWatcherEvent
        )
        if error_data is not None:
            return JSONResponse(error_data, status_code=400)
        assert confirm_watcher_request_data is not None
        app.confirm_watcher(confirm_watcher_request_data.function_name)
        return json_response()

    elif event_name == "log-function-call":
        log_function_call_request_data, error_data = await validate_request_model(
            request, LogFunctionCall
        )
        if error_data is not None:
            return JSONResponse(error_data, status_code=400)
        assert log_function_call_request_data is not None
        app.log_function_call(
            log_function_call_request_data.function_name,
            log_function_call_request_data.model_dump(),
        )
        return json_response()

    return JSONResponse({"error": "Invalid event name"}, status_code=400)


if __name__ == "__main__":
    uvicorn.run(server, host="127.0.0.1", port=8000)
