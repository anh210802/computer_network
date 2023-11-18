import os
import socket
import threading
import signal
import sys
import logging


class FileSharingClient:
    def __init__(self, host, port):

        if not self.is_valid_host(host):
            raise ValueError("Invalid host format.")
        if not self.is_valid_port(port):
            raise ValueError("Invalid port number.")

        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.upload_progress_callback = None

        signal.signal(signal.SIGINT, self.handle_sigint)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def is_valid_host(self, host):
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

    def is_valid_port(self, port):
        try:
            port = int(port)
            return 0 < port < 65536
        except ValueError:
            return False

    def set_upload_progress_callback(self, callback):
        self.upload_progress_callback = callback

    def start(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            print("Connected to the server.")

            # Start a separate thread for receiving server responses
            response_thread = threading.Thread(target=self.receive_responses, daemon=True)
            response_thread.start()

            # Start the command-shell interpreter
            self.start_command_interpreter()
        except ConnectionRefusedError:
            print(f"Error: Unable to connect to the server at {self.server_host}:{self.server_port}.")
        except Exception as e:
            print(f"Error connecting to the server: {e}")

    def receive_responses(self):
        try:
            while True:
                response = self.client_socket.recv(1024)
                try:
                    print(f"Server: {response.decode()}")
                except UnicodeDecodeError:
                    print(f"Server (raw bytes): {response}")
        except ConnectionResetError:
            print("Error: The connection with the server was unexpectedly reset.")
        except Exception as e:
            print(f"Error receiving responses: {e}")

    def handle_sigint(self, _, __):
        print("\nSIGINT received. Closing the client.")
        self.close()
        sys.exit(0)

    def start_command_interpreter(self):
        try:
            while True:
                user_input = input("Enter a command: ")

                if user_input.lower() == "exit":
                    print("\nClient closed")
                    self.close()
                    break

                if user_input.lower().startswith("upload"):
                    parts = user_input.split(" ", 1)
                    if len(parts) == 2:
                        _, filename = parts
                        filename = filename.strip()
                        if os.path.exists(filename):
                            self.upload_file(filename)
                        else:
                            print(f"Error: File '{filename}' not found.")
        except KeyboardInterrupt:
            print("\nClient closed.")
        except Exception as e:
            print(f"Error processing user input: {e}")

    def upload_file(self, filename):
        try:
            with open(filename, "rb") as file:
                file_size = os.path.getsize(filename)

                self.client_socket.send(f"sent_{filename}".encode())
                self.client_socket.send(str(file_size).encode())

                chunk_size = 1024
                total_sent = 0

                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break

                    self.client_socket.sendall(data)
                    total_sent += len(data)

                    # Calculate and update the upload progress
                    progress = total_sent / file_size
                    if self.upload_progress_callback:
                        self.upload_progress_callback(progress)

                # Signal the end of the file
                self.client_socket.send(b"<END>")
                print(f"Upload complete: {filename}")

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error uploading file: {e}")

    def close(self):
        try:
            self.client_socket.close()
        except Exception as e:
            print(f"Closing connection: {e}")


if __name__ == "__main__":
    try:
        server_host = input("Enter the server host: ")
        server_port = int(input("Enter the server port: "))

        client = FileSharingClient(server_host, server_port)

        def print_upload_progress(progress):
            print(f"Upload Progress: {progress * 100:.2f}%")

        client.set_upload_progress_callback(print_upload_progress)

        client.start()
    except ValueError as value_error:
        print(f"Error: {value_error}")
    except KeyboardInterrupt:
        print("\nClient closed.")

    