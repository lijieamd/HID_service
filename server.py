# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 16:31:08 2021

@author: yuhui
"""

import sys
import socket
import selectors
import libhid
import libconnect
import traceback

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    server = libconnect.Server(sel, conn, addr)
    hid.add_listener(server.hid_event_cb)
    sel.register(conn, selectors.EVENT_READ, data=server)

# main processing below

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} <local-port> <remote-host>")
    sys.exit(0)
    
port = int(sys.argv[1])
host = '' if sys.argv[2] == '*' else sys.argv[2]
print(f"local-port: {port}, remote-host: {sys.argv[2]}")

sel = selectors.DefaultSelector()
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
lsock.setblocking(False)
#lsock.settimeout(0.5)
sel.register(lsock, selectors.EVENT_READ, data=None)
hid = libhid.HIDManager()

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                server = key.data
                try:
                    server.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{server.addr}:\n{traceback.format_exc()}",
                    )
                    server.close()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    hid.close()
    sel.close()
    lsock.close()
    
