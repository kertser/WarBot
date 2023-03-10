# WarServer - replace HOST with 'localhost' for local testing
import socket
import WarBot

import warnings
warnings.filterwarnings("ignore")

model,tokenizer,model_punct = WarBot.initialize()

HOST = '10.0.0.125'
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f'Server is listening on port {PORT}')
    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f'Connected by {addr}')
            data = conn.recv(1024)
            received_string = data.decode()
            print(f'Received string from client: {received_string}')

            response = ""
            while not response:
                response = WarBot.get_response(received_string, model, tokenizer, model_punct, temperature=0.6)

            response_string = response

            conn.sendall(response_string.encode())
            conn.close()