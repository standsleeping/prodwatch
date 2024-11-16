import uuid
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from .rendering import render_view
from .services.watch_function import watch_function
from .inputs import parse_json_request


app = Starlette()


@app.route("/")
async def homepage_route(request: Request):
    form_url = "/watch-function"
    form_name = "watch-function-form.html"
    form_data = {"form_url": form_url}
    watch_function_form = render_view(form_name, form_data)

    response_view_name = "page.html"
    return HTMLResponse(
        render_view(
            response_view_name,
            {
                "title": "Home",
                "content": watch_function_form,
            },
        )
    )


@app.route("/watch-function", methods=["POST"])
async def watch_function_route(request: Request):
    form_data = await request.form()
    function = str(form_data.get("function"))
    function_id = str(uuid.uuid4())

    watch_function(function)

    response_view_name = "form-response.html"
    return HTMLResponse(
        render_view(
            response_view_name,
            {
                "function_id": function_id,
                "function": function,
            },
        )
    )


@app.route("/start-connection", methods=["POST"])
async def start_connection_route(request: Request):
    system_info = await parse_json_request(request)
    if system_info is None:
        return HTMLResponse("Invalid JSON data\n", status_code=400)

    print(system_info)
    return HTMLResponse("Great!\n")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
