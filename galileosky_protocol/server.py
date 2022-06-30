from .protocol import TCPRequestHandler
from datetime import datetime
import socketserver
import redis
from threading import Thread
import time
import pickle


class GalileoHandler(TCPRequestHandler):
    def process_first_packet(self, packet):
        self.server.packet_handler.first(packet)

    def process_main_packet(self, packet):
        time = packet['time']
        packet.pop('time')

        data = pickle.dumps(packet)
        last_time = pickle.loads(self.server.storage.get('lastaccepted'))

        if time < last_time:
            # если пакет пришёл с запазданием, нет смысла его обрабатывать
            self.server.storage.zadd('galileo:lose', {data: time})
            self.server.packet_handler.delayed(
                datetime.fromtimestamp(int(time)), packet)
        else:
            # добавляем пакет в очередь на обработку
            self.server.storage.zadd('galileo:process', {data: time})


# можно определить свой класс, подобно этому для обработки пакетов
class DefaultPacketHandler:
    def first(self, packet):
        print(datetime.now().time(), "- принят первый пакет:", packet)

    def delayed(self, time, packet):
        print(time.time(), "- пакет пришёл с задержкой:", packet)

    def main(self, time, packet):
        print(time.time(), "- принят основной пакет:", packet)
        return True


class GalileoServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, packet_handler=DefaultPacketHandler()):
        self.allow_reuse_address = True
        self.storage = redis.Redis(host='localhost', port=6379, db=0)
        self.packet_handler = packet_handler
        self._update_time(time.mktime(datetime.now().timetuple()))

        super().__init__(server_address, GalileoHandler)

    def accept_packets(self):
        packets = self.storage.zrange("galileo:process", 0, -1, withscores=True)

        for (b, r) in packets:
            # в зависимости от успеха обработчика добавляем пакет в принятые или потерянные
            if self._process_packet(b, r):
                self._update_time(r)
                self.storage.zadd('galileo:accept', {b: r})
            else:
                self.storage.zadd('galileo:lose', {b: r})

    def full_history(self):
        packets = self.storage.zunion(
            ["galileo:accept", "galileo:lose"], withscores=True)
        for (b, r) in packets:
            self._process_packet(b, r)

    def serve_background(self):
        self.thread = Thread(target=self.serve_forever)
        self.thread.start()

    def stop_background(self):
        self.shutdown()
        self.thread.join()
    
    def _update_time(self, accepted):
        self.storage.set('lastaccepted', pickle.dumps(accepted))

    def _process_packet(self, b, r):
        t = datetime.fromtimestamp(int(r))
        # удаляем из очереди обработанные элементы
        self.storage.zrem("galileo:process", b)

        return self.packet_handler.main(t, pickle.loads(b))
