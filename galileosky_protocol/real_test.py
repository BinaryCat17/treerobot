from .server import GalileoServer

def run():
    HOST = '0.0.0.0'
    PORT = 8080
    s = GalileoServer((HOST, PORT))
    while 1:
        s.handle_request()
        s.accept_packets()