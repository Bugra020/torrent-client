import peer
import asyncio 

class PeerManager:
    bitfield = None
    available_pieces = set()

    def __init__(self, debug_mode, info_hash, peer_id, number_of_pieces):
        self.debug_mode = debug_mode
        self.peers = peer.PeerCollection()
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.number_of_pieces = number_of_pieces
        PeerManager.bitfield = bytearray((self.number_of_pieces + 7) // 8)

    def _debug(self, msg):
        if self.debug_mode:
            print(msg)

    async def start(self, peer_list):
        self.create_peers(peer_list)
        conn_tasks = []
        for peer in self.peers:
            conn_tasks.append(asyncio.create_task(peer.connect()))
        await asyncio.gather(*conn_tasks, return_exceptions=False)

        handshake_tasks = []
        for peer in self.peers:
            handshake_tasks.append(asyncio.create_task(peer.send_handshake()))
        await asyncio.gather(*handshake_tasks, return_exceptions=False)

        #total_peer_num = self.peers.get_len()
        self.peers = [x for x in self.peers if x.healthy == False]
        #self._debug(f"{len(self.peers)}/{total_peer_num}")

        bitfield_tasks = []
        for peer in self.peers:
            bitfield_tasks.append(asyncio.create_task(peer.send_bitfield()))
        await asyncio.gather(*bitfield_tasks, return_exceptions=False)

        await self.close_all_conn()

    async def close_all_conn(self):
        for peer in self.peers:
            await peer.close_conn()        
    
    def create_peers(self, peer_list):
        for peer_data in peer_list:
            self.peers.add_peer(peer.Peer(peer_data[0], peer_data[1], self.info_hash, self.peer_id, self.number_of_pieces))
