import peer

class PeerManager():
    def __init__(self, debug_mode):
        self.peers = []
        self.debug_mode = debug_mode
    
    def _debug(self, msg):
        if self.debug_mode:
            print(msg)
    
    def connect_peers(self, peer_list):
        self._create_peers(peer_list)
        
        for peer in self.peers:
            peer.connect()

    def _create_peers(self, peer_list_data):
        for peer_data in peer_list_data:
            new_peer = peer.Peer(peer_data[0], peer_data[1], True)
            self.peers += new_peer 
