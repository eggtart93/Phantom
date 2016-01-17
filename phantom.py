#!/usr/bin/python
# phantom.py

import logging
from struct import *
from phantom_server import *
from gpio_managers import *

FORWARD_SIGNAL = 0xF0
REVERSE_SIGNAL = 0xF1
LEFT_SIGNAL = 0xF2
RIGHT_SIGNAL = 0xF3
STOP_SIGNAL = 0xF4
SHUTDOWN_SIGNAL = 0xDF
SYSTEM_CMD_SIGNAL = 0xD0
DEBUG_TEXT = 0x10
DEBUG_INT = 0x11

class Phantom(object):

    def __init__(self, config):
        self.__init_logger()
        self.server = PhantomServer(self.logger, config.HOST, config.PORT)
        self.motor_manager = MotorManager(self.logger, config)
        self.ultra_sensor_manager = None
        self.logger.info("Phantom done init")

    # with-statement support
    def __enter__(self):
        return self

    # with-statement support
    def __exit__(self, type, value, traceback):
        self.close()

    def start(self):
        self.run()

    def run(self):
        self.server.wait_for_client()

        self.running = True
        while self.running:
            response_pkt = None
            recv_pkt = self.server.receive()

            if recv_pkt is None:
                self.logger.info("Shutting down ...")
                self.running = False
                break
            elif recv_pkt[3:] == 'close':
                self.logger.info("close request received, now shutting down ...")
                self.running = False
                break
            else:
                self.logger.debug("Packet received (%d bytes):", len(recv_pkt))
                req_param, req_type = unpack("!hB", recv_pkt[0:3])
                self.logger.debug("\tPacket Header:%s", (req_param, req_type))
                self.logger.debug("\tPacket Data:%s", recv_pkt[3:])

                response_pkt = self.__handle_request(req_type, req_param)

            if response_pkt is not None:
                self.server.send(response_pkt)


    def close(self):
        self.server.close()
        logging.shutdown()

    def __init_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('phantom.log')
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

    def __handle_request(self, req_type, req_param):
        resp_type = DEBUG_TEXT
        resp_msg = ""

        if req_type == FORWARD_SIGNAL:
            resp_msg = "FORWARD_SIGNAL received"
            self.motor_manager.move_forward()

        elif req_type == REVERSE_SIGNAL:
            resp_msg = "REVERSE_SIGNAL received"
            self.motor_manager.move_backward()

        elif req_type == LEFT_SIGNAL:
            resp_msg = "LEFT_SIGNAL received"
            self.motor_manager.turn_left()

        elif req_type == RIGHT_SIGNAL:
            resp_msg = "RIGHT_SIGNAL received"
            self.motor_manager.turn_right()

        elif req_type == STOP_SIGNAL:
            resp_msg = "STOP_SIGNAL received"
            self.motor_manager.stop_movement()

        elif req_type == SHUTDOWN_SIGNAL:
            resp_msg = "SHUTDOWN_SIGNAL received"
        elif req_type == SYSTEM_CMD_SIGNAL:
            resp_msg = "SYSTEM_CMD_SIGNAL received"
        elif req_type == DEBUG_TEXT:
            resp_msg = "DEBUG_TEXT received"
        elif req_type == DEBUG_INT:
            resp_msg = "DEBUG_INT received"
        else:
            resp_msg = "Unknown Request Type %d" % req_type
            self.logger.error(resp_msg)

        print "resp_type:", resp_type, ", resp_msg:", resp_msg
        return pack("!hB%ds" % (len(resp_msg)), len(resp_msg), resp_type, resp_msg)
