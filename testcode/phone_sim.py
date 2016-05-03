import socket
import sys
import os
from struct import *

DEST_IP = "192.168.43.48"
DEST_PORT = 8080

BUF_SIZE = 1024

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
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit()
    print 'socket created'

    sock.connect((DEST_IP, DEST_PORT))
    print 'Connected to server'

    try:
        while True:
            key = raw_input("Enter (W,A,S,D):")
            key = key.upper()
            pktSend = ""
            if key == 'W':
                msg = "Forward"
                pktSend = pack("!hB%ds" % (len(msg)), len(msg), FORWARD_SIGNAL, msg)
            elif key == 'A':
                msg = "Left"
                pktSend = pack("!hB%ds" % (len(msg)), len(msg), LEFT_SIGNAL, msg)
            elif key == 'S':
                msg = "Stop"
                pktSend = pack("!hB%ds" % (len(msg)), len(msg), STOP_SIGNAL, msg)
            elif key == 'D':
                msg = "Right"
                pktSend = pack("!hB%ds" % (len(msg)), len(msg), RIGHT_SIGNAL, msg)
            else:
                print "Invalid CMD"
                continue

            if pktSend:
                try:
                    sock.sendall(pktSend)
                except socket.error:
                    print "Send failed."
                    break
            print "packet sent"

            pktRecv = sock.recv(BUF_SIZE)
            if not pktRecv:
                print "lost connection."
                break
            else:
                print "packet recv:", pktRecv

    except KeyboardInterrupt:
        print "Keyboard Interrupt"
    finally:
        sock.close()
        sys.exit()
        print "Exit"
