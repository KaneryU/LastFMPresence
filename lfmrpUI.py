#stdlib imports
import sys
import threading
# import time
import requests
#external imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import discordrp
#local imports
import lfmrp


class DownloadThread(QThread):
    signal = Signal(str)

    def __init__(self, url, index):
        QThread.__init__(self)
        self.url = url
        self.index = index

    def run(self):
        if self.url == "default":
            coverPath = "./nocover.png"
        else:
            coverPath = f"./cover{self.index}.png"
            with open(coverPath, "wb") as f:
                f.write(requests.get(self.url).content)
                
        self.signal.emit(coverPath)


class songWidget(QWidget):
    def __init__(self, song: dict, index = 0):
        super().__init__()
        self.index = index
        self.layout_ = QHBoxLayout()
        self.setLayout(self.layout_)
        self.song = song
        self.downloadThreads = []
        
        self.cover = QLabel()
        self.cover.setFixedSize(100, 100)
        self.downloadCover(song["coverInternet"])

        
        self.label = QLabel()
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setText(f"<h1>{song['top']}</h1></br><h2>{song['bottom']}</h2>")

        self.layout_.addWidget(self.cover)
        self.layout_.addWidget(self.label)
        
        
        self.setFixedHeight(150)

    def updateCover(self, coverPath):
        # Load the image
        image = QImage(coverPath)

        # Create a QPixmap object
        pixmap = QPixmap(image.size())
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a QPainter object and set its Antialiasing render hint
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Create a QPainterPath object, add a rounded rect to it and fill it with the image
        path = QPainterPath()
        path.addRoundedRect(0, 0, image.width(), image.height(), 15, 15)
        painter.fillPath(path, QBrush(image))

        # End the QPainter object
        painter.end()

        # Set the QLabel's pixmap to the rounded pixmap
        self.cover.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
    def setSong(self, song: dict):
        self.song = song
        print(f"Setting song for {self.index} to {song['top']} by {song['bottom']}")
        self.label.setText(f"<h1>{song['top']}</h1></br><h2>{song['bottom']}</h2>")
        self.downloadCover(song["coverInternet"])
        
    def downloadCover(self, url: str):
        downloadThread = DownloadThread(url, self.index)
        downloadThread.signal.connect(self.updateCover)
        downloadThread.start()

        # Store the DownloadThread object in the list
        self.downloadThreads.append(downloadThread)


class MainWindow(QMainWindow):
    updateSignal = Signal(dict)
    checkedSignal = Signal(float)
    pausePulseSignal = Signal()
    
    def __init__(self):
        super().__init__()
        self.updateSignal.connect(self.songChanged)
        self.checkedSignal.connect(self.checked)
        self.pausePulseSignal.connect(self.pausePulse)
        
        self.setWindowTitle('Last.fm Rich Presence')
        self.resize(800, 600)
        self.layout_ = QVBoxLayout()
        
        self.closeNotificatified = False
        
        self.empty = {"track": "Nothing", "artist": "Nothing", "album": "Nothing", "length": "Nothing", "human": "Nothing", "link": "https://example.com", "top": "Nothing", "bottom": "Nothing", "coverInternet": "default"}
        self.currentRaw = self.empty
        self.songWidgets = [songWidget(self.empty, i) for i in range(5)]
        
        for i in self.songWidgets:
            self.layout_.addWidget(i)
        
        self.container = QWidget()
        self.container.setLayout(self.layout_)
        
        self.setCentralWidget(self.container)
        
        lfmrp.songChangeSignal = self.updateSignal
        lfmrp.checkedSignal = self.checkedSignal
        lfmrp.pauseSignal = self.pausePulseSignal
        
        
        
        
        checkThread = threading.Thread(target=lfmrp.checkerThread, daemon=True, args=(True,))
        checkThread.start()
        
        
        
        self.menuBar_ = self.menuBar()
        
        self.statusBar_ = QStatusBar()
        
        self.setStatusBar(self.statusBar_)
        self.setMenuBar(self.menuBar_)
    @Slot()
    def songChanged(self, current: dict):
        if self.visibleRegion().isEmpty():
            if not current["track"] == "Nothing":
                self.currentRaw = current
            else:
                self.currentRaw = self.empty
            return


        # Create a new songWidget for the current song
        new_song_widget = songWidget(self.currentRaw, 0)

        # Insert the new songWidget at the top of the layout
        self.layout_.insertWidget(0, new_song_widget)

        # Insert the new songWidget at the top of the songWidgets list
        self.songWidgets.insert(0, new_song_widget)

        # Update the indices of the songWidgets
        for i, song_widget in enumerate(self.songWidgets):
            song_widget.index = i

        # Delete any songWidget whose index is greater than 4
        if len(self.songWidgets) > 5:
            widget_to_delete = self.songWidgets.pop(-1)
            widget_to_delete.deleteLater()
    
    @Slot()
    def checked(self, wait: float):
        self.statusBar_.showMessage(f"Checked for song change. Waiting {wait} seconds until next check.", int(wait * 1000) - 100) # wait is in seconds, so we need to convert it to milliseconds

    @Slot()
    def pausePulse(self):
        self.statusBar_.showMessage("Paused checking for song changes.", 2000)
        
    def changeUser(self):
        inputDialog = QInputDialog()
        inputDialog.setLabelText("Enter your Last.fm username:")
        inputDialog.textValueSelected.connect(lfmrp.changeUser)
        inputDialog.exec()
    
    def pause(self):
        lfmrp.pause()
        resumeAction.setEnabled(True)
        pauseAction.setEnabled(False)
    
    def resume(self):
        lfmrp.resume()
        resumeAction.setEnabled(False)
        pauseAction.setEnabled(True)
    
    def showEvent(self, event):
        self.songChanged(self.currentRaw)
        super().showEvent(event)
    
    def hideEvent(self, event):
        super().hideEvent(event)
    
    def closeEvent(self, event):
        self.hide()
        if not self.closeNotificatified:
            systemTray.showMessage("Last.fm Rich Presence", "Last.fm Rich Presence is still running in the background. To close it, right click the tray icon and select 'Exit'.", icon=QSystemTrayIcon.MessageIcon.Information, msecs=5000)
            self.closeNotificatified = True
            
        event.ignore()
    
    def realClose(self):
        app.exit()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowIcon(QIcon("assets/Icon.png"))
    
    
    pauseAction = QAction("Pause")
    exitAction = QAction("Exit")
    resumeAction = QAction("Resume")
    forceRefreshAction = QAction("Force Refresh")
    changeUserAction = QAction("Change User")
    
    window.menuBar_.addActions([exitAction, pauseAction, resumeAction, changeUserAction, forceRefreshAction])
    
    pauseAction.triggered.connect(window.pause)
    resumeAction.triggered.connect(window.resume)
    exitAction.triggered.connect(window.realClose)
    changeUserAction.triggered.connect(window.changeUser)
    forceRefreshAction.triggered.connect(lfmrp.forceUpdate)
    
    
            
    resumeAction.setEnabled(False)
    pauseAction.setEnabled(True)
    
    showWindow = QAction("Show Window")
    showWindow.triggered.connect(window.show)
    
    hideWindow = QAction("Hide Window")
    hideWindow.triggered.connect(window.hide)
    
    systemTray = QSystemTrayIcon()
    systemTray.setIcon(QIcon("assets/Icon.png"))
    systemTray.setVisible(True)
    systemTray.setToolTip("Last.fm Rich Presence")
    
    systemTrayMenu = QMenu()
    systemTrayMenu.addActions([pauseAction, resumeAction, forceRefreshAction, changeUserAction, showWindow, hideWindow, exitAction])
    systemTray.setContextMenu(systemTrayMenu)
    
    systemTray.show()
    systemTray.showMessage("Last.fm Rich Presence", "Last.fm Rich Presence is running in the background. Right click the tray icon to access the menu.", icon=QSystemTrayIcon.MessageIcon.Information, msecs=5000)
    
    sys.exit(app.exec())