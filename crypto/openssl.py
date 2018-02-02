#!/usr/bin/python
# -*- coding: utf-8 -*-

from ctypes import  c_char_p, c_int, c_long, byref, \
    create_string_buffer, c_void_p

import common
import util

__all__ = ['ciphers']

libcrypto = None
loaded = False

buf_size = 2048

def load_openssl():
    global loaded, libcrypto, buf, ctx_cleanup

    libcrypto = util.find_library(('crypto', 'eay32'),
                                  'EVP_get_ciphername',
                                  'libcrypto')

    if licrypto is None:














