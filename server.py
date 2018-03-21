#!/usr/bin/env python3
# Modidfied from
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter07/srv_asyncio2.py
# Asynchronous I/O inside an "asyncio" coroutine.

import asyncio, zen_utils, constants, pickle, os
from pytube import YouTube

def download_video(url):
    print('Downloading %s' % url)
    stream = YouTube(url).streams.first()
    stream.download(constants.FTP_DIR)
    return (True, stream.default_filename)

@asyncio.coroutine
def handle_conversation(reader, writer):
    address = writer.get_extra_info('peername')
    print('Accepted connection from {}'.format(address))
    while True:
        data = b''
        while not data.endswith(constants.END_SYMBOL):
            more_data = yield from reader.read(4096)
            if not more_data:
                if data:
                    print('Client {} sent {!r} but then closed'
                          .format(address, data))
                else:
                    print('Client {} closed socket normally'.format(address))
                return
            data += more_data
        # tuple: (url, option)
        tuple = pickle.loads(data[0:len(data) - 1])
        if tuple[1] == constants.OPTION_DELETE_FILES:
            file_list = tuple[0]
            for filename in file_list:
                print('Delete file:%s' % filename)
                os.remove(constants.FTP_DIR + filename)
        elif tuple[1] == constants.OPTION_DOWNLOAD_FILE:
            result = download_video(tuple[0])
            if result[0]:
                writer.write(pickle.dumps((result[1])) + constants.END_SYMBOL)
            else:
                print('Error, download file:' + tuple[0] + ' failed!')


if __name__ == '__main__':
    address = zen_utils.parse_command_line('asyncio server using coroutine')
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_conversation, *address)
    server = loop.run_until_complete(coro)
    print('Listening at {}'.format(address))
    try:
        loop.run_forever()
    finally:
        server.close()
        loop.close()
