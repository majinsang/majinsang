import socket

HOST = '0.0.0.0'
PORT = 8888

def echo_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Echo server listening on {HOST}:{PORT}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connected by {client_address}")
            
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    print(f"Received: {data.decode()}")
                    client_socket.sendall(data)
            
            print(f"Connection closed: {client_address}")

if __name__ == "__main__":
    echo_server()