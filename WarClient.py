import socket
import config # Here the constants are stored


def getReply(message):
    # Returns a reply from the server

    # Remove the endings that stuck the model
    if message.endswith("."):
        message = message.rstrip(".")
    if message.endswith(" ?"):
        message = message.replace(" ?","?")
    mesage = message.replace(" .",".")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((config.HOST, config.PORT))
            client_socket.sendall(message.encode())
            print('Wait...')
            data = client_socket.recv(1024)
            try:
                return data.decode('utf-8')
            except: #sometimes there is a problem with the decoding
                print('Decoding Error')
                return ""
            finally:
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
        except:
            return ""

if __name__ == '__main__':
    pass