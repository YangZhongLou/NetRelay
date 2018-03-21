#!/usr/bin/env python3

import argparse, random, socket, zen_utils, ftp, constants
import pickle, config


file_list = []


def get_urls():
    urls = ['https://www.youtube.com/watch?v=k9Nz2z1jTFQ&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=wENIThh7XWo&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=2',
            'https://www.youtube.com/watch?v=gLfYTP4F23g&index=3&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=ytRrjf9OPHg&index=4&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=Xi1FZZJ235I&index=5&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=bh8oVUeGMEw&index=6&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=hmBruXuXnzg&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=7',
            'https://www.youtube.com/watch?v=-mkLWm2f4hg&index=8&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=lnrMWVjxGMM&index=9&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=0u2uVld2CNA&index=10&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=6SBQ201a9R8&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=11',
            'https://www.youtube.com/watch?v=xIPKmbuVHQI&index=12&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=0AMY1EfYhqE&index=13&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=fYcpLzIPRGg&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=14',
            'https://www.youtube.com/watch?v=Wwm7j7XvdWQ&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=15',
            'https://www.youtube.com/watch?v=ZTl2G5doCv4&index=16&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=_EW-33YXTGU&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=17',
            'https://www.youtube.com/watch?v=ddx3C7779LE&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=18',
            'https://www.youtube.com/watch?v=v58ULYS_Dok&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=19',
            'https://www.youtube.com/watch?v=VKlg5sI_pxI&index=20&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=QhJhVkbCgVU&index=21&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=4BBkjzwqMSU&index=22&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=_2ksMoI4uOg&index=23&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=HweU2JXvY7A&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ&index=24',
            'https://www.youtube.com/watch?v=27IiQGuhoug&index=25&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ',
            'https://www.youtube.com/watch?v=uxYMciBcp-w&index=26&list=PLslgisHe5tBPckSYyKoU3jEA4bqiFmNBJ']
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

    # tuple: (filename,)
    tuple = pickle.loads(message[0:len(message) - 1])
    file_list.append(tuple[0])
    return tuple


def client(address):
    print('connecting ', address)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    urls = get_urls()

    # let vps download the contents you want
    for url in urls:
        sock.sendall(pickle.dumps((url, constants.OPTION_DOWNLOAD_FILE)) + constants.END_SYMBOL)
        print('Server succeeds to download url:{0}, filename:{1}'.format(url, receive(sock, constants.END_SYMBOL)))

    # using ftp to download contents from vps
    for filename in file_list:
        print('Downloading file:%s  ...' % filename)
        ftp.download(filename)

    # when downloaded, delete them all, since the limited disk space of vps
    sock.sendall(pickle.dumps((file_list, constants.OPTION_DELETE_FILES)) + constants.END_SYMBOL)
    sock.close()


if __name__ == '__main__':
    config_data = config.get_config()
    address = (config_data['server_ip'], 1060)
    client(address)
