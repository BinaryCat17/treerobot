import socketserver
import time
from .packet import parse, packet_begin, confirm, crc16

class TCPRequestHandler(socketserver.BaseRequestHandler):
    # От класса можно отнаследоваться и переопределить функции:
    # process_first_packet - вызывается, когда разобран первый пакет
    # process_main_packet - вызывается, когда разобран основной пакет

    def process_first_packet(self, packet):
        pass

    def process_main_packet(self, packet):
        pass

    def parse_packet(self, next_packed_data):
        # вспомогательная функция. сначала читает данные пакета, а потом его парсит
        packet_data, next_packed_data = self.read_packet(next_packed_data)
        if not packet_data:
            return None, bytearray()
        return parse(packet_data), next_packed_data

    def handle(self):
        try:
            # Получаем первый пакет после открытия соедниения
            # next_data для первого пакета всегда пустая
            first_packet, next_data = self.parse_packet(bytearray())
            if not first_packet:
                return None
            self.process_first_packet(first_packet[0])

            timeout = 5
            t1 = time.time()

            # получаем основные пакеты, пока не разорвётся соединение
            while 1:
                # если в пакете tcp остались данные сверх длины пакета galileosky,
                # считаем их принадлежащими следующему пакету
                main_packet, next_data = self.parse_packet(next_data)

                if not main_packet and not next_data:
                    time.sleep(1)
                    # если время ожидания вышло, завершаем соединение
                    if t1 + timeout < time.time():
                        break
                    continue

                for p in main_packet:
                    self.process_main_packet(p)

                t1 = time.time()

        except ConnectionResetError:
            return None

    def read_packet(self, next_packed_data):
        data = self.request.recv(1024)
    
        if not data and not next_packed_data:
            return None, bytearray()

        # возможно два пакета galileosky были переданы в одном пакете tcp,
        # поэтому продолжаем разбор, даже не получив новых данных
        data = next_packed_data + data

        # TODO нужно что-то сделать с is_archive и понять, для чего оно нужно
        h, length, is_archive = packet_begin(data)

        # 5 байт не учитываются в length
        length += 5

        # если заголовок не совпал, то значит что-то пошло не так
        if h != 1:
            return None, bytearray()

        # записываем данные в буфер, пока не получим пакет целиком
        while len(data) < length:
            buf = self.request.recv(1024)
            # если не смогли дочитать пакет, то ожидаем, что он дойдёт через время
            if not buf:
                return None, data + buf
            data += buf
        
        # количество оставшихся байт, отведённых под следующий пакет, 
        next_pack_size = len(data) - length
        body = data
        if next_pack_size > 0:
            # тело текущего пакета, без учета следующего
            body = data[:-next_pack_size]

        sended_crc16, real_crc16 = crc16(body)
        self.request.sendall(confirm(real_crc16))

        # если получено больше данных, чем указано в пакете, то это часть следующего пакета
        if next_pack_size > 0:
            next_packed_data = data[-next_pack_size:]
        else:
            next_packed_data = bytearray()

        # если контрольная сумма не совпала, то пропускаем пакет
        if sended_crc16 != real_crc16:
            return None, next_packed_data

        return body, next_packed_data
