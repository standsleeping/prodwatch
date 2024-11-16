import os
import uuid
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.requests import Request
from string import Template
import uvicorn


def watch_function_form(*, post_url: str) -> str:
    return render_template("watch-function-form.html", {"post_url": post_url})


def get_template(template_name: str) -> str:
    index_file_path = os.path.join(os.path.dirname(__file__), "views", template_name)
    with open(index_file_path, "r") as file:
        return file.read()


def render_template(template_name: str, data: dict) -> str:
    html_template = get_template(template_name)
    template = Template(html_template)
    rendered_html = template.substitute(data)
    return rendered_html


app = Starlette()


@app.route("/")
async def homepage(request: Request):
    form_html = watch_function_form(post_url="/watch-function")
    data = {
        "title": "Home",
        "content": form_html,
    }
    rendered_html = render_template("page.html", data)
    return HTMLResponse(rendered_html)


@app.route("/watch-function", methods=["POST"])
async def watch_function(request: Request):
    form = await request.form()
    function = form.get("function")
    function_id = str(uuid.uuid4())

    response_view = render_template(
        "form-response.html", {"function_id": function_id, "function": function}
    )

    return HTMLResponse(response_view)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
