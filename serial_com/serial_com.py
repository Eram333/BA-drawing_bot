import serial
from drawing_bot_api.config import *
import time
import setproctitle
import socket
import platform

setproctitle.setproctitle('drawing_bot_serial_com')


class Serial_communicator():
    def __init__(self):
        self.serial = self.connect_to_serial_port()
        print('Waiting until drawing bot is ready...')

        # Try for 5 seconds max
        ready_timeout = time.time() + 5
        while not self.is_ready():
            if time.time() > ready_timeout:
                print("⚠️ Timed out waiting for 'RDY'. Continuing anyway.")
                break
            time.sleep(0.5)

        print('Drawing bot is ready.')

    def check_connection(self):
        try:
            self.serial.write('_\n'.encode('utf-8'))
            return True
        except:
            print('Serial connection lost.')
            return False

    def handle_serial_commands(self, message):
        if not self.serial.is_open:
            self.reconnect()
        self.serial.write(message)
        print(f'📨 Wrote {message} to serial_port')

    def is_ready(self):
        if not self.serial.is_open:
            self.serial.open()

        self.serial.reset_input_buffer()
        self.serial.write(b'I\n')
        time.sleep(0.2)

        buffer = []
        while self.serial.in_waiting:
            byte = self.serial.read(1)
            buffer.append(byte.decode('utf-8', errors='ignore'))

        joined = ''.join(buffer)
        print(f"📥 Received from serial: {joined.strip()}")
        return 'RDY' in joined

    def restart(self):
        self.serial.write(b'R')
        self.serial.close()

    def connect_to_serial_port(self):
        while True:
            try:
                print('Connecting to serial_port...')

                if platform.system() == 'Windows':
                    serial_port = serial.Serial('COM3', BAUD, write_timeout=WRITE_TIMEOUT)
                elif platform.system() == 'Darwin':
                    serial_port = serial.Serial(USB_ID, BAUD, write_timeout=WRITE_TIMEOUT)
                elif platform.system() == 'Linux':
                    serial_port = serial.Serial('/dev/ttyUSB0', BAUD, write_timeout=WRITE_TIMEOUT)
                else:
                    raise EnvironmentError("Unsupported platform")

                print('✅ Serial port connected.')
                return serial_port

            except Exception as e:
                print(f'❌ Cannot connect to serial port: {e}')
                time.sleep(1)

    def reconnect(self):
        print('Reconnecting serial port')
        self.serial.close()
        self.serial = self.connect_to_serial_port()
        while not self.is_ready():
            time.sleep(0.5)


def main():
    serial_com = Serial_communicator()
    watchdog = time.time()

    while True:
        if (time.time() - watchdog) > 3600:
            exit(0)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if not serial_com.check_connection():
            exit()

        try:
            client_socket.connect(('localhost', 65432))
            print('✅ Socket connection established')

            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        print('🔌 Socket disconnected.')
                        client_socket.close()
                        watchdog = time.time()
                        break

                    serial_com.handle_serial_commands(data)

            except Exception as e:
                print(f'⚠️ Socket loop exception: {e}')
            finally:
                client_socket.close()

        except:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
