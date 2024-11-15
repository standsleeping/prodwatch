from .module_loader.loader import add_project_to_path, import_user_modules
from .polling.server import ServerPoller


def start_prodwatch():
    add_project_to_path()
    import_user_modules()
    poller = ServerPoller("http://localhost:3000")
    poller.start()
