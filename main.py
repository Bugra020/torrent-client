import torrent
import tracker_manager
import peer_manager
import asyncio

class Client(object):

    def __init__(self, debug_mode):
        self.torrent_file = torrent.Torrent()
        self.peer_list = []
        self.tracker_manager = tracker_manager.TrackerManager(self.torrent_file, True)
        self.debug_mode = debug_mode
    
    def _debug(self, msg):
        if self.debug_mode:
            print(msg)

    def start(self, torrent_path):
        self.torrent_file = self.torrent_file.load_from_path(torrent_path)
        self.peer_list = self.tracker_manager.get_peers()
        self._debug(self.peer_list)
        self.peer_manager = peer_manager.PeerManager(True, self.torrent_file.info_hash, self.torrent_file.peer_id, 
                                                     self.torrent_file.number_of_pieces)
        asyncio.run(self.peer_manager.connect_peers(self.peer_list))


if __name__ == '__main__':
    test_path = ("D:\\Workspace\\torrent-client\\ubuntu-22.04.5-desktop-amd64.iso.torrent")

    client = Client(True)
    client.start(test_path)