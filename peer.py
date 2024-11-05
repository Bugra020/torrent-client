import asyncio 

class PeerCollection:
    def __init__(self):
        self.peers = []

    def add_peer(self, peer):
        self.peers.append(peer)

    def __iter__(self):
        return iter(self.peers)

    def get_len(self):
        return len(self.peers)

class Peer(object):
    def __init__(self, ip, port, info_hash, peer_id):
        self.has_handshaked = False
        self.healthy = False
        self.ip = ip
        self.port = port
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.writer = None
        self.reader = None

    def _debug(self, msg):
        print(msg)

    async def connect(self):
        try:        
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            self._debug("Connected to peer ip: {} - port: {}".format(self.ip, self.port))
            self.healthy = True

        except Exception as e:
            self._debug("Failed to connect to peer (ip: %s - port: %s - %s)" % (self.ip, self.port, e.__str__()))

    async def close_conn(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send_handshake(self):
        #handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
        handshake = bytes([19]) + b"BitTorrent protocol" + (b"\x00\x00\x00\x00\x00\x00\x00\x00") + self.info_hash + self.peer_id
        try: 
            self.writer.write(handshake)
            await self.writer.drain()

            self._debug(f"handshake sent : {self.ip} {self.port}")

            response = await asyncio.wait_for(self.reader.read(68), 3)
            self._debug(f"Received handshake response {self.ip} {self.port}")

            if len(response) == 68 and response[28:48] == self.info_hash:
                self._debug(f"Handshake successful! {self.ip} {self.port}")
            else:
                self._debug(f"Handshake failed or mismatched info hash. {self.ip} {self.port}")
                self.healthy = False

        except asyncio.TimeoutError:
            self._debug(f"Timeout error {self.ip} {self.port}")
            self.writer.close()
            await self.writer.wait_closed()
        except Exception as e:
            self._debug(f"{e} error")