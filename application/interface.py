#stdlib imports
import sys
import threading
import ctypes
import enum
import json
import platform
import requests
#external imports
# from PySide6.QtGui import
# from PySide6.QtCore import
import discordrp
#local imports
import application.backend as backend
import signals
import settings

class Interface:
    ''' Interface between the backend (which runs the rich presence) and the front end (which allows for user interaction)
    All signals are emitted by the backend and connected to the front end
    All slots are connected to the backend and are called by the front end
    This is a comprehensive interface, handling all signals and slots. No direct connections are needed between the front and back end
    '''
    
    def __init__(self):
        
        self.backendThread = threading.Thread(target=backend.checkerThread)
        self.backendThread.setDaemon(True)
        
        
        
        