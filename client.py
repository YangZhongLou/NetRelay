#!/usr/bin/env python3

import argparse, random, socket, zen_utils, ftp, constants
import pickle

def get_urls():
    urls = ['https://www.youtube.com/watch?v=k9Nz2z1jTFQ&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ']
    for i in range(2, 25):
        urls.append('https://www.youtube.com/watch?v=wENIThh7XWo&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index='+ i)
    urls.append('https://www.youtube.com/watch?v=uxYMciBcp-w&index=26&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ')
    return urls


def receive(sock, suffix):
    message = sock.recv(4096)
    if not message:
        raise EOFError('socket closed')
    while not message.endswith(suffix):
        data = sock.recv(4096)
        if not data:
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message


def client(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    urls = get_urls()

    # let vps download the contents you want
    for url in urls:
        sock.sendall(pickle.dumps((url, constants.OPTION_DOWNLOAD_FILE)) + constants.END_SYMBOL)
        print(url, receive(sock, constants.END_SYMBOL))

    # using ftp to download contents from vps
    ftp.download()

    # when downloaded, delete them all, since the limited disk space of vps
    sock.sendall(pickle.dumps(('', constants.OPTION_DELETE_ALL_FILE)) + constants.END_SYMBOL)
    sock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example client')
    parser.add_argument('host', help='IP or hostname', default='198.13.59.123')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='TCP port (default 1060)')

    args = parser.parse_args()
    address = (args.host, args.p)
    client(address)
