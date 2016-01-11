#!/usr/bin/python
# config.py

import os.path

class Debug(object):
    DEBUG = True
    HOST = ""
    PORT = 8080
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
