#!/usr/bin/python
# phantom_server.py

import sys
from socket import *
from struct import *

class PhantomServer(object):

    RECV_BUFFER_SIZE = 1024

    def __init__(self, logger, host, port):
        self.host = gethostname()
        self.port = port
        self.server = socket()
        self.client = None
        self.active = False
        self.is_connected = False
        self.server.bind((host, port))
        self.logger = logger

    # with-statement support
    def __enter__(self):
        return self

    # with-statement support
    def __exit__(self, type, value, traceback):
        self.close()

    def wait_for_client(self):
        self.logger.info("Host:%s, Listening at Port:%d", self.host, self.port)
        self.server.listen(5)

        self.logger.info("Waiting for client to connect ...")

        self.client, addr = self.server.accept()
        self.logger.info("Connected by %s", str(addr))
        self.client.setblocking(1)
        self.is_connected = True

    def receive(self):
        try:
            # blocking call here
            client_pkt = self.client.recv(self.RECV_BUFFER_SIZE)
        except error as e:
            self.logger.error("recv failure:%s", e.strerror)
        else:
            if client_pkt == "":
                self.logger.error("Lost connection to client")
            else:
                return client_pkt
        return None

    def send(self, packet):
        self.client.sendall(packet)
        self.logger.debug("Packet sent. (%d bytes)", len(packet))

    def close(self):
        self.logger.debug("phantom_server.close()")
        if self.client is not None:
            self.client.close()
        if self.server is not None:
            self.server.close()

        self.client = None
        self.server = None
        self.logger = None
