from .render_html import render_html


def watch_function_form() -> str:
    form_url = "/watch-function"
    form_name = "watch-function-form.html"
    form_data = {"form_url": form_url}

    return render_html(form_name, form_data)
