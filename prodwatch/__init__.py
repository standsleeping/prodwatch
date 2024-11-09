from .ipc.server import start_ipc_server
from .module_loader.loader import add_project_to_path, import_user_modules
import threading


def start_prodwatch():
    add_project_to_path()
    import_user_modules()
    ipc_thread = threading.Thread(target=start_ipc_server)
    ipc_thread.start()
