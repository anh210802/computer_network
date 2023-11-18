import socket

SERVER_HOST = "localhost"
SERVER_PORT = 123
BUFFER_SIZE = 1024


def upload_file(client_socket, filename):
    try:
        with open(filename, "rb") as file:
            client_socket.sendall(f"UPLOAD {filename}".encode())
            response = client_socket.recv(BUFFER_SIZE).decode()

            if response.startswith("ERROR"):
                print(response)
                return

            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.sendall(data)
            print(client_socket.recv(BUFFER_SIZE).decode())
    except Exception as e:
        print(f"Error: {str(e)}")

def download_file(client_socket, filename):
    try:
        client_socket.sendall(f"DOWNLOAD {filename}".encode())
        response = client_socket.recv(BUFFER_SIZE).decode()

        if response.startswith("ERROR"):
            print(response)
            return

        _, file_name, file_size = response.split()
        file_size = int(file_size)

        with open(file_name, "wb") as file:
            while file_size > 0:
                data = client_socket.recv(BUFFER_SIZE)
                file.write(data)
                file_size -= len(data)
        print(f"File {filename} downloaded successfully")
    except Exception as e:
        print(f"Error: {str(e)}")

def list_files(client_socket):
    client_socket.sendall(b"LIST")
    file_list = client_socket.recv(BUFFER_SIZE).decode()
    print("Available files:\n" + file_list)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    while True:
        print("\nMenu:")
        print("1. Upload file")
        print("2. Download file")
        print("3. List files")
        print("4. Exit")

        choice = input("Enter your choice (1/2/3/4): ")

        if choice == "1":
            filename = input("Enter the filename to upload: ")
            upload_file(client_socket, filename)
        elif choice == "2":
            filename = input("Enter the filename to download: ")
            download_file(client_socket, filename)
        elif choice == "3":
            list_files(client_socket)
        elif choice == "4":
            client_socket.sendall(b"EXIT")
            print(client_socket.recv(BUFFER_SIZE).decode())
            client_socket.close()
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
