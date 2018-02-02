#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import sys

from crypto import rc4_md5, openssl, sodium, table

method_supported = {}
method_supported.update(rc4_md5.ciphers)
method_supported.update(openssl.ciphers)
method_supported.update(sodium.ciphers)
method_supported.update(table.ciphers)

def try_cipher(key, method = None):
    Encryptor(key, method)

def random_string(length):
    return os.urandom(length)

class Encryptor(object):
    def __init__(self, password, method):
        self.password = password
        self.key = None
        self.method = method
        self.iv_sent = False
        self.cipher_iv = b''
        self.decipher = None
        self.decipher_iv = None
        method = method.lower()
        self._method_info = self.get_method_info(method)
        if self._method_info:
            self.cipher = self.get_cipher(password, method, 1,
                                          random_string(self._method_info[1]))
        else:
            logging.error('method %s not supported' % method)
            sys.exit(1)

    def get_method_info(self, method):
        method = method.lower()
        m = method_supproted.get(method)









