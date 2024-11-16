import socket


def watch_function(function_name):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect("/tmp/prd_watch_socket")
        client.send(f"INJECT:{function_name}".encode())
        response = client.recv(1024).decode()
        print(f"Received response: {response}")
    except Exception as e:
        print(f"Error in watch_function: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    function_name = input("Enter the name of the function to log: ")
    watch_function(function_name)
