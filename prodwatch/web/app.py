import uuid
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from .rendering import render_view
from .services.watch_function import watch_function


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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
