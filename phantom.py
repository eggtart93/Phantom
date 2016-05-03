#!/usr/bin/python
# phantom.py

import os, logging
from struct import *
from config import *
from phantom_network import *
from gpio_managers import *

logging.basicConfig(level=logging.DEBUG,
        filename=APP_LOGFILE,
        filemode="w+",
        format='[%(levelname)5s](%(threadName)-s) %(message)s',
        )

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

    def __init__(self):
        init_gpio_pins()
        self.network = PhantomNetwork()
        self.motorMgr = MotorManager()
        self.ultrasonicMgr = UltrasonicManager(self.motorMgr.stop_movement)
        logging.info("Initialization completed.")

    # with-statement support
    def __enter__(self):
        return self

    # with-statement support
    def __exit__(self, type, value, traceback):
        self.shutdown()

    def start(self):
        # Block until a remote device is connected
        self.network.start()
        self.motorMgr.start()
        self.ultrasonicMgr.start()
        self.run()

    def run(self):
        # Main Loop
        warningSent = False
        logging.debug("Entering Main Loop")
        while True:
            # Check errors
            if not self.network.is_running():
                break
            if hazard_detected():
                if not warningSent:
                    warningSent = True
                    msg = "Hazard Detected!"
                    newPkt = pack("!hB%ds" % (len(msg)), len(msg), DEBUG_TEXT, msg)
                    self.network.deliver_packet(newPkt)
            else:
                warningSent = False

            # Get packet from recvQ
            packet = self.network.pickup_packet(blocking=False, timeout=0.05)
            if packet is None:
                continue

            # Unpack packet
            data_size, signal = unpack("!hB", packet[0:3])
            data = packet[3:]
            logging.debug("Header:%s\tData:%s", (data_size, signal), data)

            # Process packet
            self.handle_signal(signal, data)


    def handle_signal(self, signal, data):
        reply_type = DEBUG_TEXT
        reply = ""

        if signal == FORWARD_SIGNAL:
            reply = "FORWARD_SIGNAL received"
            self.motorMgr.move_forward()

        elif signal == REVERSE_SIGNAL:
            reply = "REVERSE_SIGNAL received"
            self.motorMgr.move_backward()

        elif signal == LEFT_SIGNAL:
            reply = "LEFT_SIGNAL received"
            self.motorMgr.turn_left()

        elif signal == RIGHT_SIGNAL:
            reply = "RIGHT_SIGNAL received"
            self.motorMgr.turn_right()

        elif signal == STOP_SIGNAL:
            reply = "STOP_SIGNAL received"
            self.motorMgr.stop_movement()

        elif signal == SHUTDOWN_SIGNAL:
            reply = "SHUTDOWN_SIGNAL received"
        elif signal == SYSTEM_CMD_SIGNAL:
            reply = "SYSTEM_CMD_SIGNAL received"
        elif signal == DEBUG_TEXT:
            reply = "DEBUG_TEXT received"
        elif signal == DEBUG_INT:
            reply = "DEBUG_INT received"
        else:
            reply = "Unknown Request Type %d" % signal
            logging.error(reply)

        newPkt = pack("!hB%ds" % (len(reply)), len(reply), reply_type, reply)
        self.network.deliver_packet(newPkt)

    def shutdown(self):
        logging.warning("shutting down ...")
        self.network.shutdown()
        self.motorMgr.shutdown()
        self.ultrasonicMgr.shutdown()
        reset_gpio_pins()
        logging.shutdown()

if __name__ == '__main__':

    logging.info("Machine Info: Host=%s, Port=%d", PhantomNetwork.LOCAL_HOST, NETWORK_PORT)

    with Phantom() as phantom:
        try:
            phantom.start()
        except KeyboardInterrupt:
            logging.warning("Keyboard Interrupt.")

    os._exit(0)
    print "Terminated"
