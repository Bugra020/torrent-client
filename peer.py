import asyncio

class PeerCollection:
    def __init__(self):
        self.peers = []

    def add_peer(self, peer):
        self.peers.append(peer)

    def __iter__(self):
        return iter(self.peers)

class Peer(object):
    def __init__(self, ip, port):
        self.has_handshaked = False
        self.healthy = False
        self.ip = ip
        self.port = port
        self.writer = ''

    def _debug(self, msg):
        print(msg)

    async def connect(self):
        try:        
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            self._debug("Connected to peer ip: {} - port: {}".format(self.ip, self.port))
            self.healthy = True

        except Exception as e:
            self._debug("Failed to connect to peer (ip: %s - port: %s - %s)" % (self.ip, self.port, e.__str__()))

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    def send_handshake(self):
        pass
    
    def send_handshake(self):
        pass
    
    def send_handshake(self):
        pass
    
    def send_handshake(self):
        pass