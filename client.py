# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 11:47:36 2021

@author: yuhui
"""

import sys
import socket
import selectors
import libconnect
import traceback

# main processing below

if len(sys.argv) != 3:
    print(f'usage: {sys.argv[0]} <remote-port> <remote-host>')
    sys.exit(0)
    
port = int(sys.argv[1])
host = sys.argv[2]
print(f'remote-port: {port}, remote-host: {sys.argv[2]}')

addr = (host, port)
sel = selectors.DefaultSelector()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex(addr)
events = selectors.EVENT_READ | selectors.EVENT_WRITE
client = libconnect.Client(sel, sock, addr)
sel.register(sock, events, data=client)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            client = key.data
            try:
                client.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{client.addr}:\n{traceback.format_exc()}",
                )
                client.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
    sock.close()