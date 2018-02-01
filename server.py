#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal

import shell

def main():
    shell.check_python()

    config = shell.get_config(False)

