import os
import socket
import threading
import inspect
from prodwatch.handle_ipc import handle_ipc, add_project_to_path, import_user_modules


def get_user_input():
    user_input = input("Enter something: ")
    print(f"You entered: {user_input}")
    return user_input


def calculate_sum(a, b):
    result = int(a) + int(b)
    print(f"{a} + {b} = {result}")
    return result


def start_ipc_server():
    if os.path.exists("/tmp/prd_watch_socket"):
        os.remove("/tmp/prd_watch_socket")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind("/tmp/prd_watch_socket")
    server.listen(1)
    conn, addr = server.accept()
    handle_ipc(conn)
    server.close()


if __name__ == "__main__":
    add_project_to_path()
    import_user_modules()

    print(f"Input module is running (PID: {os.getpid()}).")

    ipc_thread = threading.Thread(target=start_ipc_server)
    ipc_thread.start()

    try:
        while True:
            function_name = input("Enter function name to call (or 'quit' to exit): ")
            if function_name == "quit":
                break
            if function_name in globals() and callable(globals()[function_name]):
                func = globals()[function_name]
                sig = inspect.signature(func)
                args = []
                for param in sig.parameters.values():
                    arg = input(f"Enter value for {param.name}: ")
                    args.append(
                        type(param.annotation)(arg)
                        if param.annotation != inspect.Parameter.empty
                        else arg
                    )
                func(*args)
            else:
                print(f"Function {function_name} not found.")
    except KeyboardInterrupt:
        print("\nInput module stopped.")
