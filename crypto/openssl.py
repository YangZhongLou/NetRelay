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

    if libcrypto is None:
        raise Exception('libcrypto(OpenSSL) not found')

    libcrypto.EVP_get_ciphername.restype = c_void_p
    libcrypto.EVP_CIPHER_CTX_new.restype = c_void_p

    libcrypto.EVP_CipherInit_ex.argtypes = (c_void_p, c_void_p, c_char_p,
                                            c_char_p, c_char_p, c_int)

    libcrypto.EVP_CipherUpdate.argtypes = (c_void_p, c_void_p, c_void_p,
                                           c_char_p, c_int)

    try:
        libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
        ctx_cleanup = libcrypto.EVP_CIPHER_CTX_cleanup
    except AttributeError:
        libcrypto.EVP_CIPHER_CTX_reset.argtypes = (c_void_p,)
        ctx_cleanup = libcrypto.EVP_CIPHER_CTX_reset
    libcrypto.EVP_CIPHER_CTX_free.argtypes = (c_void_p,)
    if hasattr(libcrypto, 'OpenSSL_and_all_ciphers'):
        libcrypto.OpenSSL_add_all_ciphers()

    buf = create_string_buffer(buf_size)
    loaded = True















