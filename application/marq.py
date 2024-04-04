#stdlib imports
import sys
import random
#external imports
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
#local imports
#none!
        
class MarqueeLabel(QLabel):
    def __init__(self, text = '', parent = None):
        QLabel.__init__(self, parent)
        
        # self.setStyleSheet(f"background-color: rgba({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)});")
        
        self._text = text
        self._offset = 0
        self.speed = 1        
        self._timer = QTimer()
        self._timer.timeout.connect(self.advance)
        self._timer.start(1000/30)  # 30 frames per second
        
        self._format = Qt.TextFormat.PlainText
        self.lastGTSCache = (self.text() + "", self.getTextSize(self.text()))
        
    def setText(self, text):
        self._text = text
        self.resize_()
        self.update()

    def text(self):
        return self._text

    def setTextFormat(self, format: Qt.TextFormat):
        self._format = format
        self.resize_()
    
    def resize_(self):
        self.setMinimumHeight(self.getTextSizeWithCache(self.text(), self._format).height() + 5)
    
    def getTextSizeWithCache(self, txt: str, format: Qt.TextFormat) -> QSize:
        if self.lastGTSCache[0] == txt + str(format):
            pass
        else:
            self.lastGTSCache = (txt + str(format), self.getTextSize(txt))
        
        return self.lastGTSCache[1]
            
    
    def getTextSize(self, txt: str) -> QSize:
        temp = QLabel()
        temp.setTextFormat(self._format)
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
    
    def advance(self):
        fm = QFontMetrics(self.font())
        self._offset -= self.speed
        if self._offset < -self.getTextSizeWithCache(self.text(), self._format).width():
            self._offset = self.width()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._format == Qt.TextFormat.RichText:
            doc = QTextDocument()
            doc.setHtml(self._text)
            doc.setDefaultFont(self.font())
            painter.translate(self._offset, 0)
            doc.drawContents(painter)
        else:
            painter.drawText(QRect(self._offset, 0, self.width(), self.height()), Qt.AlignmentFlag.AlignVCenter, self._text)
            