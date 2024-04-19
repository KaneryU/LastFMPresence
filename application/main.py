#stdlib imports
import sys
import threading
import ctypes
import enum
import json
import platform
# import time
import requests
#external imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import discordrp
#local imports
import lfmrp
from marq import MarqueeLabel
import signals
import dialogs
import settings

def updateCheck():
    GITHUB_API_URL = "https://api.github.com/repos/kaneryu/LastFMRichPresence/releases/latest"
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        data = response.json()
        if not data["tag_name"] == "v0.1.0":
            dialog = dialogs.popupNotification("Update available", f"An update is available for Last.fm Rich Presence. You are currently running version v0.1.0, the latest version is {data['tag_name']}. You can download the latest version from the releases page.")
            dialog.exec()
    
with open("./assets/en-US.json") as f:
    lang = json.loads(f.read())  

class Language:
    def __init__(self, dict: dict) -> None:
        self.window = dict["window"]
        self.statusBar = dict["statusBar"]
        self.changeUser = dict["changeUser"]
        self.messages = dict["messages"]
        self.actions = dict["actions"]
        self.tray = dict["tray"]
    
    



class DownloadThread(QThread):
    signal = Signal(str)

    def __init__(self, url, index):
        QThread.__init__(self)
        self.url = url
        self.index = index

    def run(self):
        if self.url == "default":
            coverPath = "./assets/nocover.png"
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
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout_)
        self.song = song
        self.downloadThreads = []
        
        self.cover = QLabel()
        self.cover.setFixedSize(100, 100)
        self.downloadCover(song["coverInternet"])

        
        self.infoContainer = QWidget()
        
        self.infoLayout = QVBoxLayout()
        self.infoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.infoLayout.setSpacing(15)
        
        self.infoContainer.setLayout(self.infoLayout)
        
        self.createTopLabel(song)
        self.createBottomLabel(song) # Creates the labels and adds it to infoLayout 

        self.layout_.addWidget(self.cover)
        self.layout_.addWidget(self.infoContainer)
        
        self.setMaximumHeight(150)
        self.setMaximumWidth(600)


    def createTopLabel(self, song: dict):
        if not self.getTextSize(f"<h1>{song['top']}</h1>").width() > self.maximumWidth() - 100:        
            self.topInfo = QLabel()
            self.topInfo.setTextFormat(Qt.TextFormat.RichText)
            self.topInfo.setText(f"<h1>{song['top']}</h1>")
            self.topInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.infoLayout.addWidget(self.topInfo)
        else:
            self.topInfo = MarqueeLabel(f"<h1>{song['top']}</h1>")
            self.topInfo.speed = 3
            self.topInfo.setTextFormat(Qt.TextFormat.RichText)
            self.topInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.infoLayout.addWidget(self.topInfo)
            
    def createBottomLabel(self, song: dict): # TODO: fix the marquee label
        if not self.getTextSize(f"<h2>{song['bottom']}</h2>").width() > self.maximumWidth() - 100:
            self.bottomInfo = QLabel()
            self.bottomInfo.setTextFormat(Qt.TextFormat.RichText)
            self.bottomInfo.setText(f"<h2>{song['bottom']}</h2>")
            self.bottomInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.infoLayout.addWidget(self.bottomInfo)
        else:
            self.bottomInfo = MarqueeLabel(f"<h2>{song['bottom']}</h2>")
            self.bottomInfo.speed = 3
            self.bottomInfo.setTextFormat(Qt.TextFormat.RichText)
            self.bottomInfo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.infoLayout.addWidget(self.bottomInfo)
    
    def getTextSize(self, txt: str) -> QSize:
        temp = QLabel()
        temp.setTextFormat(Qt.TextFormat.RichText)
        temp.setFont(self.font())
        temp.setStyleSheet(self.styleSheet())
        temp.setText(txt)
        
        temp.update()
        temp.updateGeometry()
        temp.setParent(None)
        
        temp.setWindowFlags(Qt.WindowType.WindowDoesNotAcceptFocus | Qt.WindowType.WindowTransparentForInput)
        temp.setWindowFlag(Qt.WindowType.Tool)
        temp.setWindowOpacity(0)
        
        temp.show()
        return temp.size()
      
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
        self.topInfo.setText(f"<h1>{song['top']}</h1></br><h2>{song['bottom']}</h2>")
        self.downloadCover(song["coverInternet"])
        
    def downloadCover(self, url: str):
        downloadThread = DownloadThread(url, self.index)
        downloadThread.signal.connect(self.updateCover)
        downloadThread.start()

        # Store the DownloadThread object in the list
        self.downloadThreads.append(downloadThread)

    # def getTextSize(self, text):
    #     label = QLabel()
    #     label.setTextFormat(Qt.TextFormat.RichText)
    #     label.setText(text)
        
    #     fontMetrics = QFontMetrics(label.font())
    #     textSize = fontMetrics.size(0, text)
    #     return textSize

class Errors(enum.StrEnum):
    presenceCreationError = "pce"
    lastFMConnectionError = "lfme"
    
class MainWindow(QMainWindow):
    
    
    def __init__(self):
        super().__init__()
        
        signals.signals_.updateSignal.connect(self.songChanged)
        signals.signals_.checkedSignal.connect(self.checked)
        signals.signals_.pausePulseSignal.connect(self.pausePulse)
        signals.signals_.createErrorSignal.connect(self.createError)
        
        self.setWindowTitle('Last.fm Rich Presence')
        self.resize(800, 600)
        self.layout_ = QVBoxLayout()
        
        self.closeNotificatified = False
        
        self.empty = {"track": "Nothing", "artist": "Nothing", "album": "Nothing", "length": "Nothing", "human": "Nothing", "link": "https://example.com", "top": "Nothing", "bottom": "Nothing", "coverInternet": "default"}
        self.currentRaw = self.empty
        self.songWidgets = []
        
        
        self.container = QWidget()
        self.containerLayout = QVBoxLayout()
        self.container.setLayout(self.containerLayout)
        
        self.songsContainer = QWidget()
        self.songsContainer.setLayout(self.layout_)
        
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.songsContainer)
        self.scrollArea.setWidgetResizable(True)
        
        
        self.containerLayout.addWidget(self.scrollArea)
        
        self.setCentralWidget(self.container)
        
        settings.init_settings()
        
        if settings.settings.username == "":
            self.changeUser()
                
        self.checkThread = threading.Thread(target=lfmrp.checkerThread, daemon=True, args=(True,))
        self.checkThread.start()
        
        self.menuBar_ = self.menuBar()
        
        self.statusBar_ = QStatusBar()
        
        self.setStatusBar(self.statusBar_)
        self.setMenuBar(self.menuBar_)
        self.retryTimer = QTimer()
        self.retryTimer.setInterval(60_000)
        self.retryTimer.timeout.connect(self.tryCreatingPresence)

    @Slot()
    def songChanged(self, current: dict):
        if not current["track"] == "Nothing":
            self.currentRaw = current
        else:
            self.currentRaw = self.empty

        # Create a new songWidget for the current song
        new_song_widget = songWidget(self.currentRaw, 0)

        # Insert the new songWidget at the top of the layout
        self.layout_.insertWidget(0, new_song_widget)

        # Insert the new songWidget at the top of the songWidgets list
        self.songWidgets.insert(0, new_song_widget)

        # Update the indices of the songWidgets
        for i, song_widget in enumerate(self.songWidgets):
            song_widget.index = i
        
        if len(self.songWidgets) > 100:
            # Remove the last songWidget from the layout
            self.layout_.removeWidget(self.songWidgets[-1])

            # Remove the last songWidget from the songWidgets list
            self.songWidgets.pop(-1)

    def handleError(self, error: Errors):
        if error == Errors.presenceCreationError:
            if not self.retryTimer.isActive():
                dialog = dialogs.popupNotification("There was an issue contacting Discord", "The application will retry every 60 seconds untill stopped, or when the Exit button is pressed.")
                self.pause()
                dialog.exec()
        
    def tryCreatingPresence(self):
        result = lfmrp.createPresence()
        if result == True:
            self.resume()
            self.retryTimer.stop()
    
    @Slot()
    def checked(self, wait: float):
        self.statusBar_.showMessage(f"Checked for song change. Waiting {wait} seconds until next check.", int(wait * 1000) - 100) # wait is in seconds, so we need to convert it to milliseconds

    @Slot()
    def pausePulse(self):
        self.statusBar_.showMessage("Paused checking for song changes.", 2000)
    
    @Slot()  
    def changeUser(self):
        inputDialog = QInputDialog()
        inputDialog.closeEvent = lambda event: event.ignore()
        inputDialog.setWindowTitle("Change Last.fm User")
        inputDialog.setWindowIcon(QIcon("assets/Icon.png"))
        inputDialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        inputDialog.setLabelText("Enter your Last.fm username:")
        inputDialog.textValueSelected.connect(lfmrp.changeUser)
        inputDialog.exec()
    
    @Slot()
    def pause(self):
        lfmrp.pause()
        actions.resume.setEnabled(True)
        actions.pause.setEnabled(False)
    
    @Slot()
    def resume(self):
        lfmrp.resume()
        actions.resume.setEnabled(False)
        actions.pause.setEnabled(True)
    
    
    def showEvent(self, event):
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
        lfmrp.running = False
        
        self.hide() # hide all traces of the window incase the checkThread takes a while to stop
        systemTray.hide()
        self.checkThread.join()
        
        lfmrp.presence.close()
        app.exit()
    
    @Slot()
    def clearList(self):
        widget: songWidget
        for widget in reversed(self.songWidgets):
            self.layout_.removeWidget(widget)
            self.songWidgets.pop(widget)
            widget.deleteLater()
    
    @Slot()
    def createError(self, title = "An error has occured", text = "An error has occured"):
        error = QMessageBox()
        error.setWindowTitle(title)
        error.setText(text)
        error.setIcon(QMessageBox.Icon.Critical)
        error.exec()
        error.finished.connect(app.exit)

def createError(title, text):
    signals.signals_.createErrorSignal.emit(title, text)


class Actions:
    def __init__(self):
        self.pause = QAction("Pause")
        self.exit = QAction("Exit")
        self.resume = QAction("Resume")
        self.forceRefresh = QAction("Force Refresh")
        self.changeUser = QAction("Change User")
        self.clearList = QAction("Clear List")


if __name__ == '__main__':
    if platform.system() == "Windows":
        #change icon in taskbar
        myappid = u'opensource.createthesun.main.pre-release'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)
    lfmrp.createError = createError
    
    
    window = MainWindow()
    window.setWindowIcon(QIcon("assets/Icon.png"))
    app.setWindowIcon(QIcon("assets/Icon.png"))
    
    actions = Actions()
    
    window.menuBar_.addActions([actions.exit, actions.pause, actions.resume, actions.changeUser, actions.forceRefresh])
    
    actions.pause.triggered.connect(window.pause)
    actions.resume.triggered.connect(window.resume)
    actions.exit.triggered.connect(window.realClose)
    actions.changeUser.triggered.connect(window.changeUser)
    actions.forceRefresh.triggered.connect(lfmrp.forceUpdate)
    actions.clearList.triggered.connect(window.clearList)
    actions.clearList.setToolTip("Clear the recently played list")
    
            
    actions.resume.setEnabled(False)
    actions.pause.setEnabled(True)
    
    showWindow = QAction("Show Window")
    showWindow.triggered.connect(window.show)
    
    hideWindow = QAction("Hide Window")
    hideWindow.triggered.connect(window.hide)
    
    systemTray = QSystemTrayIcon()
    systemTray.setIcon(QIcon("assets/Icon.png"))
    systemTray.setVisible(True)
    systemTray.setToolTip("Last.fm Rich Presence")
    
    systemTrayMenu = QMenu()
    systemTrayMenu.addActions([actions.pause, actions.resume, actions.forceRefresh, actions.changeUser, showWindow, hideWindow, actions.exit])
    systemTray.setContextMenu(systemTrayMenu)
    
    systemTray.show()
    systemTray.showMessage("Last.fm Rich Presence", "Last.fm Rich Presence is running in the background. Right click the tray icon to access the menu.", icon=QSystemTrayIcon.MessageIcon.Information, msecs=5000)
    updateCheck()
    # first run 
    # ask user their username
    # explain usage  
    
    sys.exit(app.exec())