#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

def find_library_nt(name):
    results = []
    for directory in os.environ['PATH'].split(os.pathsep):
        fname = os.path.join(directory, name)
        if os.path.isfile(fname):
            results.append(fname)
        if fname.lower().endswith(".dll"):
            continue
        fname = fname + '.dll'
        if os.path.isfile(fname):
            results.append(fname)
    return results








