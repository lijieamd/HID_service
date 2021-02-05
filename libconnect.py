# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 10:00:06 2021

@author: yuhui
"""

import sys
import socket
import selectors
import threading

class Connection:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""

    def set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):      
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                #if sent and not self._send_buffer:
                #    self.close()

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def _read_process(self):
        print("null _read_process")
    
    def _write_process(self):
        print("null _write_process")    
    
    def read(self):
        self._read()
        self._read_process()


    def write(self):
        self._write_process()
        self._write()

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

class Server(Connection):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        
        self._msg_buffer = b""
        self.mutex = threading.Lock()
        self.msg_send_enable = False
    
    def _read_process(self):
        if self._recv_buffer:
            print(f"Server: read {len(self._recv_buffer)} bytes")
            self.msg_send_enable = True
            self.set_selector_events_mask('w')
            self._recv_buffer = b""
            
    def _write_process(self):
        self.mutex.acquire()
        if self._msg_buffer:
            print(f"Server: write {len(self._msg_buffer)} bytes")
            self._send_buffer += self._msg_buffer
            self._msg_buffer = b""
        self.mutex.release()

    def hid_event_cb(self, message):
        if self.msg_send_enable:
            self.mutex.acquire()
            self._msg_buffer += message
            self.mutex.release()    
    
        
class Client(Connection):
    def __init__(self, selector, sock, addr):
        super().__init__(selector, sock, addr)
        
        self._msg_buffer = b""
        self.mutex = threading.Lock()
        self.msg_recv_enable = False
        
    def _read_process(self):
        if self._recv_buffer:
            print(f"Client: read {len(self._recv_buffer)} bytes")
            self._recv_buffer = b""
            
    def _write_process(self):
        if not self.msg_recv_enable:
            self._send_buffer += b"client start recv request"
            self.msg_recv_enable = True
            self.set_selector_events_mask('r')

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        