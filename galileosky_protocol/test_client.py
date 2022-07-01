from datetime import datetime
import socket
import random
import struct
import time
from .packet import make_packet

def send_test_packet(data, host, port):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((host, port))

    # разбиваем отправку данных на несколько пакетов
    offset = 0
    while offset < len(data) - 10:
        tcp_client.sendall(data[offset: offset + 10])
        offset += 10
        time.sleep(0.2)

    tcp_client.sendall(data[offset:])

    received = tcp_client.recv(4)
    if(len(received) == 0):
        print("Получен пустой ответ!")
        return 0

    header, answer = struct.unpack_from('<BH', received)
    tcp_client.close()
    return answer


def gen_packet(first, time):
    tags = []

    tags.append((1, dict(hardware=random.randrange(0, 256))))
    tags.append((2, dict(firmware=random.randrange(0, 256))))
    if first:
        tags.append((3, dict(imei='862057047745531'))),
    tags.append((0x04, dict(terminal_id=random.randrange(0, 256))))
    tags.append((0x20, dict(time=time)))

    data, crc16 = make_packet(tags)
    data = bytearray(data)
    return data, crc16


def test_load(n, host, port):
    current_time = time.mktime(datetime.now().timetuple())
    data, crc16 = gen_packet(True, current_time)

    # проверяем, что контрольная сумма вычисляется правильно
    # передаём 5 байт следующего пакета galileosky вместе с текущим пакетом
    answer = send_test_packet(data, host, port)
    if answer != crc16:
        print('Контрольная сумма не совпадает!')

    # сиумуляция повреждённого пакета
    corrupted_data = bytearray(data)
    corrupted_data[10] = 0

    # проверяем, что на повреждённый пакет вернётся другая сумма
    # 5 начальных байт были переданы с предыдущей отправкой
    answer = send_test_packet(corrupted_data, host, port)
    if answer == crc16:
        print('Контрольная сумма совпала для повреждённого пакета!')

    # отправляем сразу n пакетов сразу
    for i in range(n):
        data += gen_packet(False, current_time + i)[0]

    send_test_packet(data, host, port)

HOST = "10.42.0.1"
PORT = 8080

def run():
    test_load(5, HOST, PORT)