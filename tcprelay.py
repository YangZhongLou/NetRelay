#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import socket
import errno
import struct
import logging
import traceback
import random

import encrypt
import eventloop
import shell
import common

TIMEOUT_CLEAN_SIZE = 512

MSG_FASTOPEN = 0x20000000

METHOD_NOAUTH = 0

CMD_CONNECT = 1
CMD_BIND = 2
CMD_UDP_ASSOCIATE = 3

STAGE_INIT = 0
STAGE_ADDR = 1
STAGE_UDP_ASSOC = 2
STAGE_DNS = 3
STAGE_CONNECTIING = 4
STAGE_STREAM = 5
STAGE_DESTROYED = -1

STREAM_UP = 0
STREAM_DOWN = 1

WAIT_STATUS_INIT = 0
WAIT_STATUS_READING = 1
WAIT_STATUS_WRITING = 2
WAIT_STATUS_READWRITING = WAIT_STATUS_READING | WAIT_STATUS_WRITING

BUF_SIZE = 32 * 1024

class BadSocksHeader(Exception):
    pass

class NoAcceptableMethods(Exception):
    pass

class TCPRelayHandler(object):
    def __init__(self, server, fd_to_handlers, loop, local_sock, config,
                 dns_resolver, is_local):
        self._server = server
        self._fd_to_handlers = fd_to_handlers
        self._loop = loop
        self._local_sock = local_sock
        self._remote_sock = None
        self._config = config
        self._dns_resolver = dns_resolver

        # TCP Relay works as either sslocal or ssserver
        # if is_local, this is sslocal

        self._is_local = is_local
        self._stage = STAGE_INIT
        self._encryptor = encrypt.Encryptor(config['password'],
                                            config['method'])
        self._ota_enable = config.get('one_time_auth', False)
        self._ota_enable_session = self._ota_enable
        self._ota_buff_head = b''
        self._ota_buff_data = b''
        self._ota_len = 0
        self._ota_chunk_idx = 0
        self._fastopen_connected = False
        self._data_to_write_to_local = []
        self._data_to_write_to_remote = []
        self._upstream_status = WAIT_STATUS_READING
        self._downstream_status = WAIT_STATUS_INIT
        self._client_address = local_sock.getpeername()[:2]
        self._remote_address = None
        self._forbidden_iplist = config.get('forbidden_ip')
        if is_local:
            self._chosen_server = self._get_a_server()
        fd_to_handlers[local_sock.fileno()] = self
        local_sock.setblocking(False)
        local_sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        loop.add(local_sock, eventloop.POLL_IN | eventloop.POLL_ERR,
                self._server)
        self.last_activity = 0
        self._update_activity()

    def __hash__(self):
        return id(self)

    @property
    def remote_address(self):
        return self._remote_address

    def _get_a_server(self):
        server = self._config['server']
        server_port = self._config['server_port']
        if type(server_port) == list:
            server_port = random.choice(server_port)
        if type(server) == list:
            server = random.choice(server)
        logging.debug('chosen server:%s:%d', server, server_port)
        return server, server_port

    def _update_activity(self, data_len=0):
        # tell the TCP Relay we have activities recently
        # else it will think we are inactive and timed out
        self._server.update_activity(self, data_len)

    def _update_stream(self, stream, status):
        # update a stream to a new waiting status
        # check if status is changed
        # only update if dirty
        dirty = False
        if stream == STREAM_DOWN:
            if self._downstream_status != status:
                self._downstream_status = status
                dirty = True
        elif stream == STREAM_UP:
            if self._upstream_status != status:
                self._upstream_status = status
                dirty = True
        if not dirty:
            return

        if self._local_sock:
            event = eventloop.POLL_ERR
            if self._downstream_status & WAIT_STATUS_WRITING:
                event |= eventloop.POLL_OUT
            if self._upstream_status & WAIT_STATUS_READING:
                event |= eventloop.POLL_IN
            self._loop.modify(self._local_sock, event)
        if self._remote_sock:
            event = eventloop.POLL_ERR
            if self._downstream_status & WAIT_STATUS_READING:
                event |= eventloop.POLL_IN
            if self._upstream_status & WAIT_STATUS_WRITING:
                event |= eventloop.POLL_OUT
            self._loop.modify(self._remote_sock, event)

    def _write_to_sock(self, data, sock):
        # write data to sock
        # if only some of the data are written, put remaining in the buffer
        # and update the stream to wait for writing
        if not data or not sock:
            return False
        uncomplete = False
        try:
            l = len(data)
            s = sock.send(data)
            if s < l:
                data = data[s:]
                uncomplete = True
        except (OSError, IOError) as e:
            error_no = eventloop.errno_from_exception(e)
            if error_no in (errno.EAGAIN, errno.EINPROGRESS,
                            errno.EWOULDBLOCK)
                uncomplete = True
            else:
                shell.print_exception(e)
                self.destroy()
                return False
        if uncomplete:
            if sock == self._local_sock:
                self._data_to_write_to_local.append(data)
                self._update_stream(STREAM_DOWN, WAIT_STATUS_WRITING)
            elif sock == self._remote_sock:
                self._data_to_write_to_remote.append(data)
                self._update_stream(STREAM_UP, WAIT_STATUS_WRITING)
            else:
                logging.error('write_all_to_sock:unkown socket')
        else:
            if sock == self._local_sock:
                self._update_stream(STREAM_DOWN, WAIT_STATUS_READING)
            elif sock == self._remote_sock:
                self._udpate_stream(STREAM_UP, WAIT_STATUS_READING)
            else:
                logging.error('writa_all_to_sock:unknown socket')
        return True

    def _handle_stage_connecting(self, data):
        if not self._is_local:
            if self._ota_enable_session:
                self._ota_chunk_data(data,
                                     self._data_to_write_to_remote.append)
            else:
                self._data_to_write_to_remote.append(data)
            return

        if self._ota_enable_session:
            data = self._ota_chunk_data_gen(data)
        data = self._encryptor.encrypt(data)
        self._data_to_write_to_remote.append(data)

        if self._config['fast_open'] and not self._fastopen_connected:
            # for sslocal and fastopen, we basically wait for data and use
            # send to connect
            try:
                # only connect once
                self._fastopen_connected = True
                remote_sock = \
                    self._create_remote_socket(self._chosen_server[0],
                                               self._chosen_server[1])
                self._loop.add(remote_sock, eventloop.POLL_ERR, self._server)
                data = b''.join(self._data_to_write_to_remote)
                l = len(data)
                s = remote_sock.sendto(data. MSG_FASTOPEN,
                                       self._chosen_server)
                if s < l:
                    data = data[s:]
                    self._data_to_write_to_remote = [data]
                else:
                    self._data_to_write_to_remote = []
                self._update_stream(STREAM_UP, WAIT_STATUS_READWRITING)
            except (OSError, IOError) as e:
                if eventloop.errno_from_exception(e) == errno.EINPROCESS:
                    # in this case data is not sent at all
                    self._udpate_stream(STREAM_UP, WAIT_STATUS_READWRITING)
                elif eventloop.errno_from_exception(e) == errno.ENOTCONN:
                    logging.error('fast open not supported on this OS')
                    self._config['fast_open'] = False
                    self.destroy()
                else:
                    shell.print_exception(e)
                    if self._config['verbose']:
                        traceback.print_exc()
                    self.destroy()

    @shell.exception_handle(self_=True, destroy=True, conn_err=True)
    def _handle_stage_addr(self, data):
        if self._is_local:
            cmd = common.ord(data[1])
            if cmd == CMD_UDP_ASSOCIATE:
                logging.debug('UDP associate')
                if self._local_sock.family == socket.AF_INET6:
                    header = b'\x05\x00\x00\x04'
                else:
                    header = b'\x05\x00\x00\01'
                add, port = self._local_sock.getsockname()[:2]
                addr_to_send = socket.inet_pton(self._local_sock.family,
                                                addr)
                port_to_send = struct.pack('>H', port)
                self._write_to_sock(header + addr_to_send + port_to_send,
                                    self._local_sock)
                self._stage = STAGE_UDP_ASSOC
                # just wait for the client to disconnect
                return
            elif cmd == CMD_CONNECT:
                # just trim VER CMD RSV
                data = data[3:]
            else:
                logging.error('unkown command %d', cmd)
                self.destroy()
                return
        header_result = parse_header(data)










