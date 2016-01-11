#!/usr/bin/python
# phantom_server.py

import sys
import logging
from socket import *
from struct import *

class PhantomServer(object):

    RECV_BUFFER_SIZE = 1024

    def __init__(self, host, port):
        self.host = gethostname()
        self.port = port
        self.server = socket()
        self.client = None
        self.running = False
        self.server.bind((host, port))
        self.__init_logger()
        self.logger.info("PhantomServer done init")

    # with-statement support
    def __enter__(self):
        return self

    # with-statement support
    def __exit__(self, type, value, traceback):
        self.close()

    def __init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('phantom_server.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def run(self):
        #self.logger.debug("phantom_server.run()")
        self.logger.info("Host:%s, Listening at Port:%d", self.host, self.port)
        self.server.listen(5)

        self.logger.info("Waiting for client connection ...")

        self.client, addr = self.server.accept()
        self.logger.info("Connected by %s", str(addr))

        self.client.setblocking(1)
        self.running = True
        while self.running:
            pkt_recv = self.receive()
            if pkt_recv is None:
                self.logger.info("Shutting down ...")
                self.running = False
                break
            elif pkt_recv[3:] == 'close':
                self.logger.info("close request received, now exit ...")
                break
            else:
                self.logger.debug("Packet received (%d bytes):", len(pkt_recv))
                header = unpack("!hB", pkt_recv[0:3])
                self.logger.debug("\tPacket Header:%s", header)
                self.logger.debug("\tPacket Data:%s", pkt_recv[3:])

                msg = "Hello Client"
                server_pkt = pack("!hB%ds" % (len(msg)), len(msg), 0x10, msg)
                self.client.sendall(server_pkt)
                self.logger.debug("Packet sent. (%d bytes)", len(server_pkt))

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

    def close(self):
        self.logger.debug("phantom_server.close()")
        if self.client is not None:
            self.client.close()
        if self.server is not None:
            self.server.close()

        self.client = None
        self.server = None
        logging.shutdown()
