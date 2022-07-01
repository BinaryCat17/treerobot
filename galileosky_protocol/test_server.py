from .server import GalileoServer
import time

def run():
    HOST = '0.0.0.0'
    PORT = 8080
    s = GalileoServer((HOST, PORT))
    s.serve_background()

    try:
        while 1:
            s.accept_packets()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    s.stop_background()