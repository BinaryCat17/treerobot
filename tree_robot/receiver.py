from datetime import datetime
from galileosky_protocol import GalileoServer
from robot_simulation import Storage

HOST = '0.0.0.0'
PORT = 8080


class PacketHandler:
    def __init__(self):
        self.first_lat = 0.0
        self.first_long = 0.0
        self.posx = 0
        self.posy = 0
        self.speed = 0
        self.angle = 0
        self.updated = False
        self.last_time = 0
        self.dt = 0

    def process_main_packet(self, time, packet):
        packet = packet[0]
        self.updated = True
        self.speed = packet['velocity']['speed'] / 3.6
        self.angle = packet['velocity']['angle']

        lat = packet['navigation']['lat']
        long = packet['navigation']['long']

        if self._first_lat == 0.0 and self._first_long == 0.0:
            self._first_lat = lat
            self._first_long = long

        self.posx, self.posy = Storage.latLongToXY(
            [self._first_lat, self._first_long], [lat, long])

        if self.last_time == 0:
            self.last_time = time
        else:
            self.dt = time - self.last_time
            self.last_time = time

        return True


class Receiver:
    def __init__(self):
        self._server = GalileoServer((HOST, PORT), PacketHandler())
        self._server.serve_background()

    def update(self):
        u = self.updated
        self.updated = False
        return self.updated, self.dt, u, self._server.posx, self._server.posy, self._server.speed, self._server.angle

    def stop(self):
        self._server.stop_background()
