import math
import message
import asyncio 
import struct
import peer_manager

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
    def __init__(self, ip, port, info_hash, peer_id, number_of_pieces):
        self.ip = ip
        self.port = port
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.number_of_pieces = number_of_pieces
        
        self.has_handshaked = False
        self.healthy = False
        
        self.is_choked = True
        self.is_interested = False

        self.choked_client = True
        self.client_interested = False
       
        self.bitfield = [False] * self.number_of_pieces


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

    async def listen_msg(self):
        try:
            while self.healthy:
                msg = await self.reader.read(4096)
                if not msg:
                    self._debug(f"Connection closed by peer {self.ip} {self.port}")
                    self.healthy = False
                    break

                handle_id = await message.MessageDecoder.decode(msg)
                await self.handle_msgs(handle_id, msg)

        except asyncio.CancelledError:
            self._debug(f"Listening cancelled for {self.ip} {self.port}")
        except Exception as e:
            self._debug(f"Error during message listening from {self.ip} {self.port}: {e}")

    async def send_handshake(self):
        #handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
        handshake = bytes([19]) + b"BitTorrent protocol" + (b"\x00"* 8) + self.info_hash + self.peer_id
        try: 
            self.writer.write(handshake)
            await self.writer.drain()

            self._debug(f"handshake sent : {self.ip} {self.port}")

            response = await asyncio.wait_for(self.reader.read(68), 3)
            self._debug(f"Received handshake response {self.ip} {self.port}")

            if len(response) == 68 and response[28:48] == self.info_hash:
                self._debug(f"Handshake successful! {self.ip} {self.port}")
                self.is_interested = True
                self.client_interested = True
            else:
                self._debug(f"Handshake failed or mismatched info hash. {self.ip} {self.port}")
                self.healthy = False
                await self.close_conn()
            
            await self.listen_msg()

        except asyncio.TimeoutError:
            self._debug(f"Timeout error {self.ip} {self.port}")
            await self.close_conn()
        except Exception as e:
            self._debug(f"{e} error")

    async def send_bitfield(self):
        bitfield = peer_manager.PeerManager.bitfield
        msg_length = 1 + len(bitfield)
        msg_id = 5

        bitfield_msg = struct.pack(">Ib", msg_length, msg_id) + bitfield
        
        try:    
            self.writer.write(bitfield_msg)
            await self.writer.drain()
        except Exception as e:
            self._debug(f"error while trying to send bitfield {e} {self.ip} {self.port}")
        
        self._debug(f"bitfield message sent succesfully {self.ip} {self.port}")

    async def handle_msgs(self, msg_id, msg):
        match msg_id:
            case 0:
                await self.handle_choke()
            case 1:
                await self.handle_unChoke()
            case 2:
               await self.handle_interested() 
            case 3:
                await self.handle_notInterested() 
            case 4:
                await self.handle_have(msg)
            case 5:
               await self.handle_bitfield(msg) 
            case 6:
                #await self.handle_request()
                pass
            case 7:
                #await self.handle_piece()
                pass
            case 8:
                #await self.handle_cancel()
                pass
            case 9:
                #await self.handle_port()
                pass
    
    async def handle_choke(self):
        self._debug(f"Received 'Choke' message from peer {self.ip}")
        self.choked_client = True
        # await self.cancel_pending_requests()

    async def handle_unChoke(self):
        self._debug(f"Received 'UnChoke' message from peer {self.ip}")
        self.choked_client = False
        # await self.send_piece_requests()
        

    async def handle_interested(self):
        self.is_interested = True
        self._debug(f"{self.ip} is interested")

        # unchoking algorithm here
    
    async def handle_notInterested(self):
        self._debug(f"Received 'Not Interested' message from peer {self.ip}")

        # Update the peer state to reflect that the peer is not interested
        self.is_interested = False

        # await self.cancel_pending_requests()

    
    async def handle_have(self, msg):
        piece_index = int.from_bytes(msg[1:5], byteorder='big')
        
        self.bitfield[piece_index] = True
        
        self._debug(f"added available piece at index {piece_index} from HAVE message")
        peer_manager.PeerManager.available_pieces.add(piece_index)

    async def handle_bitfield(self, msg):
        payload = msg[5:]
        expected_length = math.ceil(self.number_of_pieces/ 8)

        if len(payload) < expected_length:
            self._debug(f"Invalid Bitfield length: {len(payload)} bytes. Expected: {expected_length} bytes.")
            raise ValueError("Invalid Bitfield message length")
        
        total_bits = self.number_of_pieces
        current_bit_index = 0

        for byte in payload:
            for i in range(8):
                if current_bit_index < total_bits:
                    bit = (byte >> (7 - i)) & 1
                    self.bitfield.append(bit == 1)
                    current_bit_index += 1
                else:
                    break

        for index, bit in enumerate(self.bitfield):
            if bit:
                peer_manager.PeerManager.available_pieces.add(index)
                #self._debug(f"added available piece at index {index}")