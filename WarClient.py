import socket

HOST = 'localhost'
PORT = 5000

message = "Это хорошо, но глядя на ролик, когда ефиопские толпы в Израиле громят машины и нападают на улице на израильтян - задумаешься, куда все движется"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    client_socket.sendall(message.encode())
    print('Wait...')
    data = client_socket.recv(1024)
    received_string = data.decode('utf-8')
    print(f'Received string from server: {received_string}')