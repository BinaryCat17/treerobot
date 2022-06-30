from galileosky_protocol import SimpleTCPServer
from galileosky_protocol import TCPRequestHandler
from treerobot import Storage

HOST = '0.0.0.0'
PORT = 8080

class Handler (TCPRequestHandler):
    def __init__(self, request, client_address, server):
        server.first_lat = 0.0
        server.first_long = 0.0
        server.updated = False
        super().__init__(request, client_address, server)

    def process_first_packet(self, packet):
        print("Пришёл первый пакет:", packet)

    def process_main_packet(self, packet):
        print("Пришёл основной пакет:", packet)
        packet = packet[0]
        self.server.updated = True
        self.server.speed = packet['velocity']['speed'] / 3.6
        self.server.angle = packet['velocity']['angle']

        lat = packet['navigation']['lat']
        long = packet['navigation']['long']

        if self._first_lat == 0.0 and self._first_long == 0.0:
            self._first_lat = lat
            self._first_long = long
        
        self.server.posx, self.server.posy = Storage.latLongToXY([self._first_lat, self._first_long], [lat, long])


class Receiver:
    def __init__(self):
        self._server = SimpleTCPServer((HOST, PORT), Handler)
        self._server.serve_background()
        self.posx = 0
        self.posy = 0
        self.speed = 0
        self.angle = 0

    def update(self):
        u = self.updated
        self.updated = False
        return u, self.posx, self.posy, self.speed, self.angle

    def stop(self):
        self._server.stop_background()
       




