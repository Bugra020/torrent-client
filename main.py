import torrent

def run(torrent_path):

    torrent_file = torrent.Torrent().load_from_path(torrent_path)

if __name__ == '__main__':
    run("D:\\Workspace\\torrent-client\\test.torrent")