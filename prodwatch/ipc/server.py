import socket
import os
from prodwatch.watcher.function_watcher import FunctionWatcher


def handle_ipc(conn):
    watcher = FunctionWatcher()

    while True:
        data = conn.recv(1024).decode().split(":")
        command = data[0]

        if command == "WATCH":
            function_name = data[1]
            success = watcher.watch_function(function_name)
            conn.send("SUCCESS".encode() if success else "FUNCTION_NOT_FOUND".encode())

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
