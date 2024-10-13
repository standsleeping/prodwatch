import os
import socket
import threading
import inspect


def get_user_input():
    user_input = input("Enter something: ")
    print(f"You entered: {user_input}")
    return user_input


def calculate_sum(a, b):
    result = int(a) + int(b)
    print(f"{a} + {b} = {result}")
    return result


def handle_ipc(conn):
    while True:
        data = conn.recv(1024).decode().split(":")
        command = data[0]

        if command == "INJECT":
            function_name = data[1]
            if function_name in globals() and callable(globals()[function_name]):
                original_function = globals()[function_name]

                def logged_function(*args, **kwargs):
                    result = original_function(*args, **kwargs)
                    try:
                        with open(
                            os.environ.get("APP_LOG_FILE", "/app/log_file.txt"), "a"
                        ) as f:
                            f.write(
                                f"Function {function_name} called with args: {args}, kwargs: {kwargs}, result: {result}\n"
                            )
                        print(f"Logged {function_name} call")
                    except Exception as e:
                        print(f"Error writing to log file: {e}")
                    return result

                globals()[function_name] = logged_function
                conn.send("SUCCESS".encode())
            else:
                conn.send("FUNCTION_NOT_FOUND".encode())

        elif command == "STOP":
            break

    conn.close()


def start_ipc_server():
    if os.path.exists("/tmp/input_module_socket"):
        os.remove("/tmp/input_module_socket")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind("/tmp/input_module_socket")
    server.listen(1)
    conn, addr = server.accept()
    handle_ipc(conn)
    server.close()


if __name__ == "__main__":
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
