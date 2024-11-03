
class PeerManager():
    def __init__(self):
        self.peers = []
    
    def _debug(self, msg):
        if self.debug_mode:
            print(msg)
    
    def connect_peers(self, peer_list):
        pass