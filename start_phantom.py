#!/usr/bin/python
# start_phantom.py

import config
from phantom_server import PhantomServer

if __name__ == '__main__':
    print "Host:", config.Debug.HOST, "Port:", config.Debug.PORT
    print "type(config.Debug.HOST) = ", type(config.Debug.HOST)
    print "type(config.Debug.PORT) = ", type(config.Debug.PORT)
    
    with PhantomServer(config.Debug.HOST, config.Debug.PORT) as server:
        server.run()
