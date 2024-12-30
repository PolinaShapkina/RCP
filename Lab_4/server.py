import socket
import threading
import time


class UDPSender:
    def __init__(self, multicast_group, port, message_file):
        self.multicast_group = multicast_group
        self.port = port
        self.message_file = message_file
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def send_message(self):
        while True:
            with open(self.message_file, 'r') as file:
                message = file.read().strip()
            self.server_socket.sendto(message.encode(), (self.multicast_group, self.port))
            print(f"Отправлено сообщение: {message}")
            time.sleep(10)


class IntermediateClient:
    def __init__(self, multicast_group, port):
        self.multicast_group = multicast_group
        self.port = port
        self.message_history = []
        self.lock = threading.Lock()

    def udp_listener(self):
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener_socket.bind(('', self.port))
        
        mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton('0.0.0.0')
        listener_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print("UDP слушатель запущен, ожидает сообщения.")
        
        while True:
            data, _ = listener_socket.recvfrom(1024)
            message = data.decode()
            with self.lock:
                if message not in self.message_history:
                    self.message_history.append(message)
                    if len(self.message_history) > 5:
                        self.message_history.pop(0)
                    print(f"Новое сообщение: {message}")

    def tcp_server(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(('', 1503))
        tcp_socket.listen(1)

        while True:
            conn, _ = tcp_socket.accept()
            with conn:
                with self.lock:
                    messages_to_send = '\n'.join(self.message_history).encode()
                conn.sendall(messages_to_send)


if __name__ == "__main__":
    multicast_group = '233.0.0.1'
    port = 1502
    message_file = 'message.txt'  # Файл с сообщением

    # Запуск сервера в отдельном потоке
    udp_sender = UDPSender(multicast_group, port, message_file)
    threading.Thread(target=udp_sender.send_message, daemon=True).start()

    # Запуск промежуточного клиента в отдельном потоке
    intermediate_client = IntermediateClient(multicast_group, port)
    threading.Thread(target=intermediate_client.udp_listener, daemon=True).start()
    threading.Thread(target=intermediate_client.tcp_server, daemon=True).start()

    # Приложение будет работать до его завершения
    while True:
        time.sleep(1)  # Защита от завершения программы
