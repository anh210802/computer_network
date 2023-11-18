import socket

def start_client():
    # Define the server address (IP and port)
    server_address = ('127.0.0.1', 12345)

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect(server_address)
    print("Connected to {}:{}".format(*server_address))

    # Request a file from the server
    file_name = input("Enter the file name: ")
    client_socket.send(file_name.encode('utf-8'))

    # Receive the file data
    with open('received_' + file_name, 'wb') as file:
        print("Receiving file...")
        chunk = client_socket.recv(1024)
        while chunk:
            file.write(chunk)
            chunk = client_socket.recv(1024)
        print("File received successfully")

    # Close the connection
    client_socket.close()

if __name__ == "__main__":
    start_client()
