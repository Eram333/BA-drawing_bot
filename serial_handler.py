import socket
import time
from drawing_bot_api.config import *

class Serial_handler:

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_socket.settimeout(20)
        self.server_socket.bind(('localhost', 65432))
        self.server_socket.listen()
        self.conn = None
        self.addr = None
        self.buffer = []

    def __init_connection(self):
        print("📡 Waiting for serial_com.py connection...")
        self.conn, self.addr = self.server_socket.accept()
        print('✅ Connected to serial script.')

    def __disconnect(self):
        if self.conn is not None:
            self.conn.close()

    def send_buffer(self, promting):
        self.__init_connection()
        __time = self.millis()

        # Send first two items (likely handshake/setup)
        self.conn.sendall(str(self.buffer[0]).encode('utf-8'))
        self.conn.sendall(str(self.buffer[1]).encode('utf-8'))
        time.sleep(0.5)

        if promting:
            answer = input('Do you want to continue with this drawing? (y/n)\n')
            if answer.lower() != 'y':
                self.buffer.clear()
                return 1

        for message in self.buffer:
            try:
                self.conn.sendall(str(message).encode('utf-8'))
            except Exception as e:
                print(f"⚠️ Failed to send: {e}")

            __delay = SERIAL_DELAY - ((self.millis() - __time) / 1000)
            time.sleep(max(__delay, 0))
            __time = self.millis()

        self.buffer.clear()
        self.__disconnect()

    def millis(self):
        return time.time() * 1000

    def __call__(self, message):
        self.buffer.append(message)

if __name__ == '__main__':
    serial_handler = Serial_handler()
    serial_handler.__init_connection()