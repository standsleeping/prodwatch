import socket


def inject_logging(function_name):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect("/tmp/prd_watch_socket")
        client.send(f"INJECT:{function_name}".encode())
        response = client.recv(1024).decode()
        print(f"Received response: {response}")
    except Exception as e:
        print(f"Error in inject_logging: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    function_name = input("Enter the name of the function to log: ")
    inject_logging(function_name)
