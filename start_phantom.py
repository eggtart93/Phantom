#!/usr/bin/python
# start_phantom.py

import config
from phantom import Phantom

if __name__ == '__main__':
    print "Host:", config.Debug.HOST, "Port:", config.Debug.PORT

    with Phantom(config.Debug) as phantom:
        phantom.start()
