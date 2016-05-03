import os
import logging
from struct import *
from config import *
from phantom_network import *

logging.basicConfig(level=logging.DEBUG,
        #filename=APP_LOGFILE,
        #filemode='w'
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

if __name__ == '__main__':
    logging.info("Machine Info: Host=%s, Port=%d", PhantomNetwork.LOCAL_HOST, NETWORK_PORT)
    network = PhantomNetwork()
    try:
        network.start()
        while True:
            if not network.running:
                break

            packet = network.pickup_packet(blocking=False, timeout=0.5)
            if packet is None:
                continue
            data_size, signal = unpack("!hB", packet[0:3])
            data = packet[3:]
            logging.debug("Header:%s\tData:%s", (data_size, signal), data)

            msg = "Testing!"
            newPkt = pack("!hB%ds" % (len(msg)), len(msg), DEBUG_TEXT, msg)
            network.deliver_packet(newPkt)

    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt")
        network.shutdown()
        #os._exit(1)
    else:
        network.shutdown()
        logging.info("Normal Exit")
