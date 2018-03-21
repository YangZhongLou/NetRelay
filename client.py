#!/usr/bin/env python3

import argparse, random, socket, zen_utils, ftp, constants
import pickle, config


file_list = []


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

    # tuple: (filename, option)
    tuple = pickle.loads(message[0:len(data) - 2])
    file_list.append(tuple[1])
    return tuple


def client(address):
    print('connecting ', address)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    urls = get_urls()

    # let vps download the contents you want
    for url in urls:
        sock.sendall(pickle.dumps((url, constants.OPTION_DOWNLOAD_FILE)) + constants.END_SYMBOL)
        print(url, receive(sock, constants.END_SYMBOL))

    # using ftp to download contents from vps
    for filename in file_list:
        print('Downloading file:%s...' % filename)
        ftp.download(filename)

    # when downloaded, delete them all, since the limited disk space of vps
    sock.sendall(pickle.dumps((file_list, constants.OPTION_DELETE_FILES)) + constants.END_SYMBOL)
    sock.close()


if __name__ == '__main__':
    config_data = config.get_config()
    address = (config_data['server_ip'], 1060)
    client(address)
