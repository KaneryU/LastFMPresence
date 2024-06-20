# stdlib imports
import sys
import random
import dataclasses
import requests
import signals
import settings
import threading
import backend as backend_
import enum
# library imports
from PySide6.QtCore import Qt, Signal as QSignal, Slot as Slot, QObject, QAbstractListModel, QModelIndex, QTimer, Property as Property, QByteArray
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QInputDialog, QMessageBox, QSystemTrayIcon, QMenu, QApplication
from PySide6.QtQml import QQmlApplicationEngine
# local imports
import dialogs

def updateCheck():
    GITHUB_API_URL = "https://api.github.com/repos/kaneryu/LastFMRichPresence/releases/latest"
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        data = response.json()
        if not data["tag_name"] == "v0.1.0":
            dialog = dialogs.popupNotification("Update available", f"An update is available for Last.fm Rich Presence. You are currently running version v0.1.0, the latest version is {data['tag_name']}. You can download the latest version from the releases page.")
            dialog.exec()

            
@dataclasses.dataclass
class SongItem:
    title: str = ""
    artist: str = ""
    album: str = ""
    imagePath: str = ""
    
class SongListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._songs = []

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if 0 <= index.row() < self.rowCount():
            song = self._songs[index.row()]
            name = self.roleNames().get(role)
            if name:
                return getattr(song, name.decode())

    def roleNames(self) -> dict[int, QByteArray]:
        d = {}
        for i, field in enumerate(dataclasses.fields(SongItem)):
            d[Qt.ItemDataRole.DisplayRole + i] = field.name.encode()
        return d

    def rowCount(self, parent=None):
        return len(self._songs)

    def addSong(self, song: SongItem):
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._songs.insert(0, song)
        self.endInsertRows()
        
    def moveSong(self, fromIndex: int, toIndex: int):
        self.beginMoveRows(QModelIndex(), fromIndex, fromIndex, QModelIndex(), toIndex)
        self._songs.insert(toIndex, self._songs.pop(fromIndex))
        self.endMoveRows()
    
    def clear(self):
        self.beginResetModel()
        self._songs.clear()
        self.endResetModel()

class Errors(enum.StrEnum):
    presenceCreationError = "pce"
    lastFMConnectionError = "lfme"

class Backend(QObject):
    modelChanged = QSignal(QAbstractListModel, name="modelChanged", arguments=['model'])
    statusChanged = QSignal(str, name="statusChanged", arguments=['status_'])
    def __init__(self):
        super().__init__()
        
        signals.signals_.updateSignal.connect(self.songChanged)
        signals.signals_.checkedSignal.connect(self.checked)
        signals.signals_.pausePulseSignal.connect(self.pausePulse)
        signals.signals_.createErrorSignal.connect(self.createError)
        signals.signals_.checkedSignal.connect(self.checked)
        signals.signals_.pausePulseSignal.connect(self.pausePulse)
        
        self.closeNotificatified = False
        
        self.empty = {"track": "Nothing", "artist": "Nothing", "album": "Nothing", "length": "Nothing", "human": "Nothing", "link": "https://example.com", "top": "Nothing", "bottom": "Nothing", "coverInternet": "default"}
        self.currentRaw = self.empty

        
        self.model = SongListModel()
        
        settings.init_settings()
        
        if settings.settings.username == "":
            self.changeUser()
                
        self.checkThread = threading.Thread(target=backend_.checkerThread, daemon=True, args=(True,))
        self.checkThread.start()
        

    @Slot()
    def songChanged(self, current: dict):
        if not current["track"] == "Nothing":
            self.currentRaw = current
        else:
            self.currentRaw = self.empty
            
        title = self.currentRaw["track"]
        artist = self.currentRaw["artist"]
        album = self.currentRaw["album"]
        imagePath = self.currentRaw["coverInternet"]
        s = SongItem(title, artist, album, imagePath)
        self.model.addSong(s)
        print("added song")
        


    def handleError(self, error: Errors):
        if error == Errors.presenceCreationError:
            if not self.retryTimer.isActive():
                dialog = dialogs.popupNotification("There was an issue contacting Discord", "The application will retry every 60 seconds untill stopped, or when the Exit button is pressed.")
                self.pause()
                dialog.exec()
        
    def tryCreatingPresence(self):
        result = backend_.createPresence()
        if result == True:
            self.resume()
            self.retryTimer.stop()
    
    @Slot()
    def checked(self, wait: float):
        pass

    @Slot()
    def pausePulse(self):
        pass
    
    @Slot()  
    def changeUser(self):
        inputDialog = QInputDialog()
        inputDialog.closeEvent = lambda event: event.ignore()
        inputDialog.setWindowTitle("Change Last.fm User")
        inputDialog.setWindowIcon(QIcon("assets/Icon.png"))
        inputDialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        inputDialog.setLabelText("Enter your Last.fm username:")
        inputDialog.textValueSelected.connect(backend_.changeUser)
        inputDialog.exec()
    
    @Slot()
    def pause(self):
        backend_.pause()
        # actions.resume.setEnabled(True)
        # actions.pause.setEnabled(False)
    
    @Slot()
    def resume(self):
        backend_.resume()
        # actions.resume.setEnabled(False)
        # actions.pause.setEnabled(True)
    

    
    def closeEvent(self):
        engine.rootObjects()[0].hide()
        
        if not self.closeNotificatified:
            systemTray.showMessage("Last.fm Rich Presence", "Last.fm Rich Presence is still running in the background. To close it, right click the tray icon and select 'Exit'.", icon=QSystemTrayIcon.MessageIcon.Information, msecs=5000)
            self.closeNotificatified = True

    
    def realClose(self):
        backend_.running = False
        
        engine.rootObjects()[0].hide()
        systemTray.hide()
        self.checkThread.join()
        
        backend_.presence.close()
        app.exit()
        engine.quit.emit()
    
    @Slot()
    def clearList(self):
        SongListModel.clear()
    
    @Slot()
    def createError(self, title = "An error has occured", text = "An error has occured"):
        error = QMessageBox()
        error.setWindowTitle(title)
        error.setText(text)
        error.setIcon(QMessageBox.Icon.Critical)
        error.exec()
        error.finished.connect(app.exit)
        
    @Slot(str, result=str)
    def getVersion(self, version):
        return version

    @Slot(None, result=None)
    def exit(self):
        self.realClose()
    
    @Slot(None, result=None)
    def minimize(self):
        self.closeEvent()
    
    @Slot(None, result=None)
    def maximize(self):
        engine.rootObjects()[0].show()
    
    @Slot(None, result=None)
    def pause(self):
        backend_.pause()
    
    @Slot(None, result=None)
    def resume(self):
        backend_.resume()
    
    @Slot(None, result=None)
    def forceRefresh(self):
        backend_.lastPlayingHash = ""
        
    @Slot(None, result=None)
    def changeUser_(self):
        self.changeUser()
    
    @Slot(None, result=None)
    def clearList(self):
        self.model.clear()
    
    @Slot()
    def checked(self, wait: float):
        self.statusChanged.emit(f"Checked for song change. Waiting {wait} seconds until next check.") # wait is in seconds, so we need to convert it to milliseconds

    @Slot()
    def pausePulse(self):
        self.statusChanged.emit("Paused checking for song changes.")

class Actions:
    def __init__(self):
        self.pause = QAction("Pause")
        self.exit = QAction("Exit")
        self.resume = QAction("Resume")
        self.forceRefresh = QAction("Force Refresh")
        self.changeUser = QAction("Change User")
        self.clearList = QAction("Clear List")
    
if __name__ == '__main__':
    app = QApplication()
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    engine.load('main.qml')
    engine.rootObjects()[0].hide()
    
    backend = Backend()
    engine.rootObjects()[0].setProperty('backend', backend)

    mod = backend.model
    backend.modelChanged.emit(mod)
    
    # timer = QTimer()
    # timer.timeout.connect(lambda: addRandomSong(mod))
    # timer.start(1000)
    
    actions = Actions()
    
    actions.pause.triggered.connect(backend.pause)
    actions.resume.triggered.connect(backend.resume)
    actions.exit.triggered.connect(backend.realClose)
    actions.changeUser.triggered.connect(backend.changeUser)
    actions.forceRefresh.triggered.connect(backend.forceRefresh)
    actions.clearList.triggered.connect(backend.clearList)
    actions.clearList.setToolTip("Clear the recently played list")
    
    systemTray = QSystemTrayIcon()
    systemTray.setIcon(QIcon("assets/Icon.png"))
    systemTray.setVisible(True)
    systemTray.setToolTip("Last.fm Rich Presence")
    
    showWindow = QAction("Show Window")
    showWindow.triggered.connect(backend.maximize)
    
    hideWindow = QAction("Hide Window")
    hideWindow.triggered.connect(backend.minimize)
    
    systemTrayMenu = QMenu()
    systemTrayMenu.addActions([actions.pause, actions.resume, actions.forceRefresh, actions.changeUser, showWindow, hideWindow, actions.exit])
    systemTray.setContextMenu(systemTrayMenu)
    
    systemTray.show()
    systemTray.showMessage("Last.fm Rich Presence", "Last.fm Rich Presence is running in the background. Right click the tray icon to access the menu.", icon=QSystemTrayIcon.MessageIcon.Information, msecs=5000)

    sys.exit(app.exec())