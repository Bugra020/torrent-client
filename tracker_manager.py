import struct
import random
import socket

class TrackerManager(object):
    def __init__(self, torrent_file, debug_mode):
        self.torrent_file = torrent_file
        self.debug_mode = debug_mode

    def _debug(self, msg):
        if self.debug_mode:
            print(msg)

    def get_peers(self):
        peers = []
        tracker_peers = []
        for url in self.torrent_file.announce_list:
            type = url[:3]
            try:
                match type:
                    case 'udp':
                        tracker_peers = self._get_udp_peer(url)
                    case 'htt':
                        #peers.append(self._get_http_peer(url))
                        pass
                    case _:
                        self._debug(f"{url} tracker url is not valid")
            except TimeoutError:
                pass

            for peer in tracker_peers:
                peers.append(peer)
        
        return peers
        
    
    def _get_udp_peer(self, url):
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
                    peers = self._parse_tracker_response(response[20:])
                    self._debug(f"got the peers from {host} succesfully")
                    return peers
                except Exception as e:
                    self._debug(f"{host} error occured : {e}")
                finally:
                    sock.close()

            except TimeoutError:
                self._debug(f"{host} Attempt {attempt + 1} timed out. Retrying...")
            except Exception as e:
                self._debug(f"{host} error occured : {e}")

        raise TimeoutError("Tracker did not respond after multiple attempts")

    def _get_http_peer(self, url):
        pass

    def _parse_tracker_response(self, response):
        peers = []
        for i in range(0, len(response), 6):
            ip_address = '.'.join(map(str, response[i:i+4]))

            port = struct.unpack(">H", response[i+4:i+6])[0]
            
            peers.append((ip_address, port))
        
        return peers
