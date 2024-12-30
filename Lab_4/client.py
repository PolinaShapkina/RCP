import socket
import tkinter as tk


class FinalClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            data = s.recv(1024)
            return data.decode().splitlines()

    def create_ui(self):
        root = tk.Tk()
        root.title("Конечный Клиент")

        messages_text = tk.Text(root, width=50, height=15)
        messages_text.pack()

        def fetch_messages():
            messages = self.get_messages()
            messages_text.delete(1.0, tk.END)
            messages_text.insert(tk.END, '\n'.join(messages))

        fetch_button = tk.Button(root, text="Получить сообщения", command=fetch_messages)
        fetch_button.pack()

        root.mainloop()


if __name__ == "__main__":
    final_client = FinalClient('localhost', 1503)
    final_client.create_ui()
