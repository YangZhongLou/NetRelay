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










