import gradio as gr
import socket

HOST = '129.159.146.88'
PORT = 5000

def sendToServer(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(message.encode())
        # print('Wait...')
        data = client_socket.recv(1024)
        try:
            return data.decode('utf-8')
            # print(f'Received string from server: {received_string}')
        except:  # sometimes there is a problem with the decoding
            return "Бот устал и должен отдохнуть"
            # print('decoding error, please try again')
        finally:
            client_socket.close()

def clear_textbox():
    return ""

with gr.Blocks() as WarBot:
    gr.Markdown(
        """   
        # Боевой Чат-Бот портала WarOnline
        Пока-что это бредогенератор, тренированый на диалогах форума,<br>
        Есть куча багов. Но мы работаем над улучшениями! :)
        """)

    with gr.Row():
        input = gr.Textbox(lines=5, placeholder="Введите сообщение...", label="Вопрос:")
        output = gr.Textbox(label="Ответ:", lines=5)

    send_btn = gr.Button("Послать Сообщение")
    send_btn.click(fn=sendToServer, inputs=input, outputs=output)
    clr_btn = gr.Button("Очистить")
    clr_btn.click(fn=clear_textbox,outputs=input)


WarBot.launch()
