import socket

class Peer(object):

    def __init__(self, ip, port, debug_mode):
        self.ip = ip
        self.port  = port
        self.debug_mode = debug_mode

    def _debug(self, msg):
        if self.debug_mode:
            print(msg)

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port), timeout=2)
            self.socket.setblocking(False)
            self._debug("Connected to peer ip: {} - port: {}".format(self.ip, self.port))
            self.healthy = True

        except Exception as e:
            self._debug("Failed to connect to peer (ip: %s - port: %s - %s)" % (self.ip, self.port, e.__str__()))
            return False

        return True

    def send_handshake(self):
        pass
    
    def send_handshake(self):
        pass
    
    def send_handshake(self):
        pass
    
    def send_handshake(self):
        pass