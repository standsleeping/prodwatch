from .module_loader.loader import add_project_to_path, import_user_modules
from .polling.server import ServerPoller


def start_prodwatch():
    server_url = "http://localhost:3000"
    poller = ServerPoller(server_url)

    if not poller.check_connection():
        return

    add_project_to_path()
    import_user_modules()
    poller.start()
