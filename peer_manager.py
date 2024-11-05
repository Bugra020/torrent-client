import peer
import asyncio

class PeerManager():
    def __init__(self, debug_mode):
        self.debug_mode = debug_mode
        self.peers = peer.PeerCollection()
    
    def _debug(self, msg):
        if self.debug_mode:
            print(msg)
    
    async def connect_peers(self, peer_list):
        self.create_peers(peer_list)
        tasks = []
        for peer in self.peers:
            tasks.append(asyncio.create_task(peer.connect()))
        await asyncio.gather(*tasks, return_exceptions=False)
        for peer in self.peers:
            await peer.close()
    
    def create_peers(self, peer_list):
        for peer_data in peer_list:
            self.peers.add_peer(peer.Peer(ip=peer_data[0], port=peer_data[1]))
