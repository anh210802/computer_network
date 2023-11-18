import socket
import os

SERVER_HOST = "localhost"
SERVER_PORT = 123
BUFFER_SIZE = 1024
UPLOADS_FOLDER = "uploads"

def handle_upload(client_socket, filename):
    try:
        with open(os.path.join(UPLOADS_FOLDER, filename), "wb") as file:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
            client_socket.sendall(b"OK File uploaded successfully")
    except Exception as e:
        error_message = f"ERROR {str(e)}"
        print(error_message)
        client_socket.sendall(error_message.encode())


def handle_download(client_socket, filename):
    try:
        file_path = os.path.join(UPLOADS_FOLDER, filename)
        file_size = os.path.getsize(file_path)
        client_socket.sendall(f"FILE {filename} {file_size}".encode())

        with open(file_path, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.sendall(data)
    except Exception as e:
        client_socket.sendall(f"ERROR {str(e)}".encode())

def handle_list(client_socket):
    files = os.listdir(UPLOADS_FOLDER)
    file_list = "\n".join(files)
    client_socket.sendall(file_list.encode())

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(1)
    server_socket.settimeout(60)  # Set a timeout of 60 seconds

    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        request = client_socket.recv(BUFFER_SIZE).decode()
        command, *args = request.split()

        if command == "UPLOAD":
            handle_upload(client_socket, args[0])
        elif command == "DOWNLOAD":
            handle_download(client_socket, args[0])
        elif command == "LIST":
            handle_list(client_socket)
        elif command == "EXIT":
            client_socket.sendall(b"OK Goodbye")
            client_socket.close()
            break
        else:
            client_socket.sendall(b"ERROR Invalid command")

        client_socket.close()

if __name__ == "__main__":
    if not os.path.exists(UPLOADS_FOLDER):
        os.makedirs(UPLOADS_FOLDER)
    main()
