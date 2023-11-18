import socket
import threading
import tqdm
import logging


class FileSharingServer:
    BUFFER_SIZE = 1024

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            logging.info(f"New connection from {client_address}")

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        # Add the client to the list of connected clients
        client_address = client_socket.getpeername()
        with self.lock:
            self.clients[client_address] = client_socket

        # Start a thread to receive responses from the client
        response_thread = threading.Thread(target=self.receive_responses, args=(client_socket,), daemon=True)
        response_thread.start()

        try:
            while True:
                data = client_socket.recv(self.BUFFER_SIZE)
                if not data:
                    break  # Connection closed by client

                # Process the received data
                logging.info(f"Received data from {client_address}: {data.decode()}")

                # Process the file
                self.receive_file(client_socket)
        except ConnectionResetError:
            logging.info(f"Connection reset by {client_address}")
        except Exception as e:
            logging.info(f"Error handling client {client_address}: {e}")

        finally:
            # Remove the client from the list when the connection is closed
            with self.lock:
                del self.clients[client_address]
            client_socket.close()
            logging.info(f"Connection closed by {client_address}")

    def receive_responses(self, client_socket):
        try:
            while True:
                response = client_socket.recv(self.BUFFER_SIZE)
                try:
                    logging.info(f"Client {client_socket.getpeername()}: {response.decode('utf-8')}")
                except UnicodeDecodeError:
                    logging.info(f"Client {client_socket.getpeername()} (raw bytes): {response}")
        except OSError as _:
            # Ignore OSError when client_socket is closed
            pass
        except Exception as e:
            print(f"Error receiving responses from {client_socket.getpeername()}: {e}")
        finally:
            if not client_socket._closed:
                print(f"Response thread terminated for {client_socket.getpeername()}")

    def receive_file(self, client_socket):
        file_name = client_socket.recv(self.BUFFER_SIZE).decode()
        logging.info("[*] Receiving:", file_name)
        file_size = client_socket.recv(self.BUFFER_SIZE).decode()
        print("[*] File size:", file_size)

        with open(file_name, "wb") as file:
            file_bytes = b""
            done = False
            progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000,
                                 total=int(file_size))
            while not done:
                data = client_socket.recv(self.BUFFER_SIZE)
                if data[-5:] == b"<END>":
                    done = True
                    file.write(file_bytes)
                else:
                    file_bytes += data
                    progress.update(self.BUFFER_SIZE)
            print("[*] File received successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = FileSharingServer('localhost', 123)
    server.start()

