#!/usr/bin/python
# phantom_server.py

import sys
import socket
import threading
import Queue
import logging
from config import *

class PhantomNetwork(object):
    """ Network Module """
    LOCAL_HOST = socket.gethostbyname(socket.gethostname())

    def __init__(self):
        self.recvQ = Queue.Queue()
        self.sendQ = Queue.Queue()
        self.client = None
        self.rxThread = None
        self.txThread = None
        self.running = False
        self.runningRLock = threading.RLock()

    # with-statement support
    def __enter__(self):
        return self

    # with-statement support
    def __exit__(self, type, value, traceback):
        self.shutdown()

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((NETWORK_HOST, NETWORK_PORT))
        except socket.error as e:
            logging.error("Socket bind failed: " + e.strerror)
            return False
        server.listen(2)
        logging.info("Host:%s, Listening to Port:%d", self.LOCAL_HOST, NETWORK_PORT)

        self.client, addr = server.accept()
        logging.info("Connected by %s", str(addr))

        # configure socket
        self.client.setblocking(0)
        self.client.settimeout(NETWORK_TIMEOUT)

        # spawn 2 threads for receiver and transmitter
        self.set_running(True)
        self.rxThread = threading.Thread(name="RxThread", target=self.receiver)
        self.txThread = threading.Thread(name="TxThread", target=self.transmitter)
        self.rxThread.start()
        self.txThread.start()

        # close server and stop listening for any incoming connections
        server.close()
        logging.info("Receiver and Transmitter has started.")
        return True

    def set_running(self, flag):
        self.runningRLock.acquire()
        self.running = flag
        self.runningRLock.release()

    def is_running(self):
        return self.running

    def pickup_packet(self, blocking=True, timeout=None):
        try:
            packet = self.recvQ.get(blocking, timeout)
            self.recvQ.task_done()
        except Queue.Empty:
            return None
        return packet

    def deliver_packet(self, packet, blocking=True):
        try:
            packet = self.sendQ.put(packet, blocking)
        except Queue.Full:
            logging.error("Deliver failure, FIFO queue is full!")
            return False
        return True

    def shutdown(self):
        logging.debug("PhantomNetwork.shutdown()")
        self.set_running(False)
        if self.rxThread and self.rxThread.isAlive():
            self.rxThread.join()
        if self.txThread and self.txThread.isAlive():
            self.txThread.join()
        if self.client is not None:
            self.client.close()
            logging.debug("Network socket closed")
        self.client = None
        logging.warning("Network Module has been shutdown.")

    def receiver(self):
        while self.running:
            try:
                # blocking call here
                packet = self.client.recv(NETWORK_BUFFER_SIZE)
            except socket.timeout:
                continue
                #logging.warning("receive nothing (%d sec)", NETWORK_TIMEOUT)
            except socket.error, error:
                logging.error("receive failure:%d, %s", error[0], error[1])
                self.set_running(False)
                break

            if packet == "":
                logging.error("Lost connection to client, closing receiver")
                self.set_running(False)
                break

            logging.debug("receiver:%s", str(packet))
            self.recvQ.put(packet)
        logging.debug("Exits from receiver()")

    def transmitter(self):
        blocking = False
        timeout = 3
        while self.running:
            try:
                packet = self.sendQ.get(blocking, timeout)
            except Queue.Empty:
                continue

            try:
                self.client.sendall(packet)
                logging.debug("transmitter:%s", str(packet))
            except socket.timeout:
                logging.warning("transmit operation timeout (%d sec)", NETWORK_TIMEOUT)
            except socket.error, error:
                logging.error("transmit failure:%d, %s", error[0], error[1])
                self.set_running(False)
                break

            self.sendQ.task_done()
        logging.debug("Exits from transmitter()")
