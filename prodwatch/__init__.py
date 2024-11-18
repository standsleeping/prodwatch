from .module_loader.loader import add_project_to_path, import_user_modules
from .manager import Manager


def start_prodwatch():
    base_server_url = "http://localhost:8000"
    manager = Manager(base_server_url)

    if not manager.check_connection():
        return

    add_project_to_path()
    import_user_modules()
    manager.start()
