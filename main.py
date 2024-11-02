import torrent
import tracker_manager

class Client(object):

    def __init__(self, debug_mode):
        self.torrent_file = torrent.Torrent()
        self.tracker_manager = tracker_manager.TrackerManager(self.torrent_file, True)
        self.peer_list = []
        self.debug_mode = debug_mode
    
    def _debug(self, msg):
        if self.debug_mode:
            print(msg)

    def start(self, torrent_path):
        self.torrent_file = self.torrent_file.load_from_path(torrent_path)
        self.peer_list = self.tracker_manager.get_peers()
        self._debug(self.peer_list)


if __name__ == '__main__':
    test_path = ("D:\\Workspace\\torrent-client\\[LimeTorrents.lol]Age.of.Empires"
                 ".II.Definitive.Edition..v101.102.42346.0.#107882.11.DLCs.Bonuse"
                 "s..MULTi17..[FitGirl.Repack..Selective.Download.-.from.6.5.GB]."
                 "torrent")

    client = Client(True)
    client.start(test_path)