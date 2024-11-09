import os
import sys
import importlib
import socket
import threading


def find_function(function_name):
    for name, module in sys.modules.items():
        if module is None:
            continue
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            if callable(func):
                return module, func
    return None, None


def handle_ipc(conn):
    while True:
        data = conn.recv(1024).decode().split(":")
        command = data[0]

        if command == "INJECT":
            function_name = data[1]
            print(f"Injecting {function_name}")

            module, original_function = find_function(function_name)
            print(f"Module: {module}, Original function: {original_function}")

            if module and original_function:

                def logged_function(*args, **kwargs):
                    result = original_function(*args, **kwargs)
                    try:
                        with open(
                            os.environ.get("APP_LOG_FILE", "/app/log_file.txt"), "a"
                        ) as f:
                            f.write(
                                f"Function {module.__name__}.{function_name} called with args: {args}, kwargs: {kwargs}, result: {result}\n"
                            )
                        print(f"Logged {module.__name__}.{function_name} call")
                    except Exception as e:
                        print(f"Error writing to log file: {e}")
                    return result

                setattr(module, function_name, logged_function)
                conn.send("SUCCESS".encode())
            else:
                conn.send("FUNCTION_NOT_FOUND".encode())

        elif command == "STOP":
            break

    conn.close()


def start_ipc_server():
    if os.path.exists("/tmp/prd_watch_socket"):
        os.remove("/tmp/prd_watch_socket")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind("/tmp/prd_watch_socket")
    server.listen(1)
    conn, addr = server.accept()
    handle_ipc(conn)
    server.close()


def import_user_modules():
    project_root = os.getcwd()
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".py"):
                module_path = os.path.relpath(os.path.join(root, file), project_root)
                module_name = module_path[:-3].replace(os.path.sep, ".")
                print(f"Importing {module_name}")
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    print(f"Failed to import {module_name}")
                except Exception as e:
                    print(f"Error attempting import of {module_name}: {e}")


def add_project_to_path():
    project_root = os.getcwd()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def start_prodwatch():
    add_project_to_path()
    import_user_modules()
    ipc_thread = threading.Thread(target=start_ipc_server)
    ipc_thread.start()
