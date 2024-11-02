import torrent
import struct
import random
import socket
import time

class Client(object):

    def __init__(self):
        self.torrent_file = torrent.Torrent()
        self.peer_list = []
    
    def start(self, torrent_path):
        self.torrent_file = self.torrent_file.load_from_path(torrent_path)
        self.get_peers()
        print(self.peer_list)

    def get_peers(self):
        peers = []
        tracker_peers = []
        for url in self.torrent_file.announce_list:
            type = url[:3]
            try:
                match type:
                    case 'udp':
                        tracker_peers = self.get_udp_peer(url)
                    case 'htt':
                        peers.append(self.get_http_peer(url))
                    case _:
                        print("tracker url is not valid")
            except TimeoutError:
                pass

            for peer in tracker_peers:
                peers.append(peer)
        
        self.peer_list = peers
        
    
    def get_udp_peer(self, url):
        host, port = url.replace("udp://", "").replace("/announce", "").split(":")
        port = int(port)

        # Prepare the connection and transaction IDs
        connection_id = 0x41727101980  # Protocol ID for UDP connect request
        transaction_id = random.randint(0, 0xFFFFFFFF)

        retries = 1
        for attempt in range(retries):
            try:
                # Create a UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                try:
                    # Step 1: Send Connect Request
                    connect_request = struct.pack(">QII", connection_id, 0, transaction_id)
                    sock.sendto(connect_request, (host, port))

                    # Receive Connect Response
                    response, _ = sock.recvfrom(16)
                    action, recv_transaction_id, connection_id = struct.unpack(">IIQ", response)
                    
                    if recv_transaction_id != transaction_id or action != 0:
                        raise ValueError("Invalid connect response")

                    # Step 2: Send Announce Request
                    transaction_id = random.randint(0, 0xFFFFFFFF)
                    params = (
                        connection_id,
                        1,  # Action: announce
                        transaction_id,
                        self.torrent_file.info_hash[:20],
                        self.torrent_file.peer_id[:20],
                        0,  # downloaded
                        self.torrent_file.total_length,  # left
                        0,  # uploaded
                        0,  # event: 0 (none)
                        0,  # IP address: 0 (default)
                        0,  # key: random for anti-spoofing, can use 0 here
                        0xFFFFFFFF, # num_want: -1 (default, requesting more peers)
                        6881  # port
                    )
                    announce_request = struct.pack(">QII20s20sQQQIIIIH", *params)
                    sock.sendto(announce_request, (host, port))

                    # Receive Announce Response
                    response, _ = sock.recvfrom(65535)  # Read enough for header + some peers
                    action, recv_transaction_id, interval, leechers, seeders = struct.unpack(">IIIII", response[:20])
                    
                    if recv_transaction_id != transaction_id or action != 1:
                        raise ValueError("Invalid announce response")

                    # Parse the list of peers
                    peers = self.parse_tracker_response(response[20:])
                    print(f"got the peers from {host} succesfully")
                    return peers

                finally:
                    sock.close()

            except TimeoutError:
                print(f"{host} Attempt {attempt + 1} timed out. Retrying...")
            except:
                print(f"{host} error occured")
                retries = 0

        raise TimeoutError("Tracker did not respond after multiple attempts")


    def parse_tracker_response(self, response):
        peers = []
        # Each peer entry is 6 bytes: 4 for IP, 2 for port
        for i in range(0, len(response), 6):
            # Extract the IP address from the first 4 bytes
            ip_address = '.'.join(map(str, response[i:i+4]))
            
            # Extract the port from the last 2 bytes
            port = struct.unpack(">H", response[i+4:i+6])[0]
            
            # Append the IP and port as a tuple to the list of peers
            peers.append((ip_address, port))
        
        return peers

    def get_http_peer(self, url):
        pass

if __name__ == '__main__':
    test_path = ("D:\\Workspace\\torrent-client\\[LimeTorrents.lol]Age.of.Empires"
                 ".II.Definitive.Edition..v101.102.42346.0.#107882.11.DLCs.Bonuse"
                 "s..MULTi17..[FitGirl.Repack..Selective.Download.-.from.6.5.GB]."
                 "torrent")

    client = Client()
    client.start(test_path)