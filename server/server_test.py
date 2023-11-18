import socket
import os

def start_server():
    # Define the server address (IP and port)
    server_address = ('127.0.0.1', 12345)

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the server address
    server_socket.bind(server_address)

    # Listen for incoming connections (max 5 connections in the queue)
    server_socket.listen(5)
    print("Server is listening on {}:{}".format(*server_address))

    while True:
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from {}:{}".format(*client_address))

        # Handle the client's request
        handle_client(client_socket)

def handle_client(client_socket):
    # Receive the file name from the client
    file_name = client_socket.recv(1024).decode('utf-8')
    print("Received file request: {}".format(file_name))

    try:
        # Open the requested file in binary mode
        with open(file_name, 'rb') as file:
            # Read and send the file in chunks
            chunk = file.read(1024)
            while chunk:
                client_socket.send(chunk)
                chunk = file.read(1024)
            print("File sent successfully")

    except FileNotFoundError:
        print("File not found")
        client_socket.send(b'File not found')

    finally:
        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    start_server()
