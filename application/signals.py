from PySide6.QtCore import Signal, QObject
import enum

class Errors(enum.StrEnum):
    presenceCreationError = "pce"
    lastFMConnectionError = "lfme"
    
class Signals(QObject):
    _instance = None  # Private variable to store the instance

    updateSignal: Signal = Signal(dict)
    checkedSignal: Signal = Signal(float)
    pausePulseSignal: Signal = Signal()
    createErrorSignal: Signal = Signal(str, str)
    handleErrorSignal: Signal = Signal(Errors)

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