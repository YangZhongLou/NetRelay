#!/usr/bin/python
# -*- coding: utf-8 -*-

import  string
import  struct
import  hashlib

__all__ = ['ciphers']

cached_tables = {}

if hasattr(string, 'maketrans'):
    maketrans = string.maketrans
    translate = string.translate
else:
    maketrans = bytes.maketrans
    translate = bytes.translate

def get_table(key):
    m = hashlib.md5()
    m.update(key)
    s = m.digest()
    a, b = struct.unpack('<QQ', s)
    table = maketrans(b'', b'')
    table = [table[i: i + 1] for i in range(len(table))]
    for i in range(1, 1024):
        table.sort(key=lambda  x: int(a % (ord(x) + i)))
    return table

def init_table(key):
    if key not in cached_tables:
        encrypt_table = b''.join(get_table(key))
        decrypt_table = maketrans(encrypt_table, maketrans(b'', b''))
        cached_tables[key] = [encrypt_table, decrypt_table]
    return cached_tables[key]

class TableCipher(object):
    def __init__(self, cipher_name, key, iv, op):
        self._encrypt_table, self._decrypt_table = init_table(key)
        self._op = op

    def update(self, data):
        if self._op:
            return translate(data, self._encrypt_table)
        else:
            return translate(data, self._decrypt_table)

ciphers = {
    'table': (0, 0, TableCipher)
}