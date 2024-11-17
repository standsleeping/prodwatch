import os
from string import Template


def get_template(template_name: str) -> str:
    index_file_path = os.path.join(os.path.dirname(__file__), "html", template_name)
    with open(index_file_path, "r") as file:
        return file.read()


def render_html(template_name: str, data: dict[str, str]) -> str:
    html_template = get_template(template_name)
    template = Template(html_template)
    rendered_html = template.substitute(data)
    return rendered_html
