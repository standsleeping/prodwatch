from .module_loader.loader import add_project_to_path, import_user_modules
from .listener import Listener


def start_prodwatch():
    base_listening_url = "http://localhost:3000"
    listener = Listener(base_listening_url)

    if not listener.check_connection():
        return

    add_project_to_path()
    import_user_modules()
    listener.start()
