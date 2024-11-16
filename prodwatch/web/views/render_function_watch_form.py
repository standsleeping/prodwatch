from .render_view import render_view


def render_function_watch_form():
    form_url = "/watch-function"
    form_name = "watch-function-form.html"
    form_data = {"form_url": form_url}

    return render_view(form_name, form_data)
