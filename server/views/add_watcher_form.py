from .render_html import render_html


def add_watcher_form() -> str:
    form_url = "/add-watcher"
    form_name = "add-watcher-form.html"
    form_data = {"form_url": form_url}

    return render_html(form_name, form_data)
