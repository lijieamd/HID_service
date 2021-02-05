# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 10:52:59 2021

@author: yuhui
"""

import mouse
import keyboard
import threading
import traceback

class HIDManager:
    def __init__(self):
        self._listener = []
        self.mutex = threading.Lock()
        self._hook()
        
    def __del__(self):
        self.close()
    
    def close(self):
        self._listener.clear()
        self._unhook()
    
    def add_listener(self, handler):
        self._listener.append(handler)
        
    def remove_listener(self, handler):
        self._listener.remove(handler)
    
    def _mouse_cb(self, event):
        #print(f'type: {type(event)}, event: {event}')
        # 1. encode event message
        message = b"test mouse event message"
        # 2. send to each listener
        for handler in self._listener:
           try:
               self.mutex.acquire()
               handler(message)
               self.mutex.release()
           except Exception:
               traceback.print_exc()

    def _key_cb(self, event):
        #print(f'type: {type(event)}, event: {event}')
        # 1. encode event message
        message = b"test key event message"
        # 2. send to each listener
        for handler in self._listener:
           try:
               self.mutex.acquire()
               handler(message)
               self.mutex.release()
           except Exception:
               traceback.print_exc()
    
    def _hook(self):
        self._unhook() # prevent multiple hook
        mouse.hook(self._mouse_cb)
        keyboard.hook(self._key_cb)
    
    def _unhook(self):
        mouse.unhook_all()
        keyboard.unhook_all()