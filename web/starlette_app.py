import uvicorn
from typing import TypeVar, Callable, Any, TypeAlias, Awaitable
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from app import ProdwatchApp
from .views.render_html import render_html
from .views.process_list import process_list
from .views.add_watcher_form import add_watcher_form


class ProcessInfo(BaseModel):
    instance_id: str


class SystemInfo(BaseModel):
    process: ProcessInfo


class AddProcessRequest(BaseModel):
    system_info: SystemInfo


class WatchSuccessRequest(BaseModel):
    function_name: str


class FunctionCallRequest(BaseModel):
    function_name: str
    args: list = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)


T = TypeVar("T", bound=BaseModel)
RouteHandler_T: TypeAlias = Callable[[Request, T], Awaitable[Any]]
ValidatedRouteHandler_T: TypeAlias = Callable[[Request], Awaitable[Any]]


class RouteHandler:
    """Utility class to handle common route operations with schema validation"""

    @staticmethod
    def render_page(title: str, content: str) -> HTMLResponse:
        return HTMLResponse(
            render_html("page.html", {"title": title, "content": content})
        )

    @staticmethod
    def json_response(message: str = "Success", status_code: int = 200) -> JSONResponse:
        return JSONResponse(message + "\n", status_code=status_code)

    @staticmethod
    async def validate_request_model(
        request: Request, model_class: type[T]
    ) -> tuple[T | None, JSONResponse | None]:
        """Validates request data against a Pydantic model"""
        try:
            data = await request.json()
            validated_data = model_class.model_validate(data)
            return validated_data, None
        except Exception as e:
            error_message = {"error": "Invalid request data", "details": str(e)}
            return None, JSONResponse(error_message, status_code=400)


def require_validated_json(
    model_class: type[T],
) -> Callable[[RouteHandler_T[T]], ValidatedRouteHandler_T]:
    """Decorator to validate request data against a Pydantic model"""

    def decorator(handler: RouteHandler_T[T]) -> ValidatedRouteHandler_T:
        async def wrapper(request: Request) -> Any:
            validated_data, error_response = await RouteHandler.validate_request_model(
                request, model_class
            )
            if error_response is not None:
                return error_response
            # At this point, we know validated_data cannot be None
            assert validated_data is not None
            return await handler(request, validated_data)

        return wrapper

    return decorator


server = Starlette()
app = ProdwatchApp()


@server.route("/")
async def root(request: Request):
    form_html = add_watcher_form()
    process_ids = app.get_process_ids()
    list_container = process_list(process_ids)
    return RouteHandler.render_page("Home", form_html + list_container)


@server.route("/add-watcher", methods=["POST"])
async def add_watcher(request: Request):
    form_data = await request.form()
    function_name = str(form_data.get("function_name"))
    app.add_watcher(function_name)
    return RouteHandler.render_page("Form Response", "<div>Watcher added</div>")


@server.route("/add-process", methods=["POST"])
@require_validated_json(AddProcessRequest)
async def add_process(request: Request, data: AddProcessRequest):
    instance_id = data.system_info.process.instance_id
    app.add_process(instance_id)
    return RouteHandler.json_response()


@server.route("/pending-function-names", methods=["GET"])
async def pending_function_names(request: Request):
    pending_function_names = app.get_pending_function_names()
    response = {"function_names": list(pending_function_names)}
    return JSONResponse(response, status_code=200)


@server.route("/confirm-watcher", methods=["POST"])
@require_validated_json(WatchSuccessRequest)
async def confirm_watcher(request: Request, data: WatchSuccessRequest):
    app.confirm_watcher(data.function_name)
    return RouteHandler.json_response()


@server.route("/log-function-call", methods=["POST"])
@require_validated_json(FunctionCallRequest)
async def function_call_route(request: Request, data: FunctionCallRequest):
    app.log_function_call(data.function_name, data.model_dump())
    print(f"Received {data.function_name} call")
    return RouteHandler.json_response()


if __name__ == "__main__":
    uvicorn.run(server, host="127.0.0.1", port=8000)
