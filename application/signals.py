from PySide6.QtCore import Signal, QObject
import enum

class Errors(enum.StrEnum):
    presenceCreationError = "pce"
    lastFMConnectionError = "lfme"
    
class Signals(QObject):
    _instance = None  # Private variable to store the instance

    updateSignal: Signal = Signal(dict) # Signal emitted when the backend has updated the currently playing song
    checkedSignal: Signal = Signal(float) # Signal emitted when the backend has checked the currently playing song
    pausePulseSignal: Signal = Signal() # Signal emitted occasionaly when checking is paused
    createErrorSignal: Signal = Signal(str, str) # Signal emitted when a fatal error occurs in the backend
    handleErrorSignal: Signal = Signal(Errors) # Signal emitted when a non-fatal error occurs in the backend

    # def __init__(self):
    #     print("Created")
    #     super().__init__()
    
    # @staticmethod
    # def get_instance():
    #     print("try get instance")
    #     if Signals._instance is None:
    #         print("failed; creating new one")
    #         Signals._instance = Signals()
    #     return Signals._instance

signals_: Signals = Signals()