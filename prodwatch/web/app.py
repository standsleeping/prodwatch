import uuid
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from .rendering import render_view


app = Starlette()


@app.route("/")
async def homepage(request: Request):
    form_url = "/watch-function"
    form_name = "watch-function-form.html"
    form_data = {"form_url": form_url}
    watch_function_form = render_view(form_name, form_data)
    page_data = {
        "title": "Home",
        "content": watch_function_form,
    }
    page = render_view("page.html", page_data)
    return HTMLResponse(page)


@app.route("/watch-function", methods=["POST"])
async def watch_function(request: Request):
    form_data = await request.form()
    function = form_data.get("function")
    function_id = str(uuid.uuid4())

    response_view = render_view(
        "form-response.html", {"function_id": function_id, "function": function}
    )

    return HTMLResponse(response_view)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
