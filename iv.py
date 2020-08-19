#!/usr/bin/env python

# v.1.6
# separated menu to a standalone class to enable mouse es
# 1.8
# image functions including rotations and flips
# dual menus

import os, sys, time, signal, math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from menu import *
from c import *

from runit import *

# global settings
N = 0

def signal_handler(signal, frame):
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

class IV(QWidget):

    def __init__(self, parent=None):
        super(IV, self).__init__(parent)

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._tip = None
        self._top = True
        self._time1 = self.digitTime()
        self._time2 = self.digitTime() + '...'
        self._tb1 = None
        self._tb2 = None
        self.f = None
        self.opacity = 1
        
        self.threadpool = QThreadPool()        
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())                

        # ratio
        self.factor = 1.0
        self.rin = 1.1
        self.rout = 0.9

        self.image = QImage()
        self.tmp = 'tmp.png'
        self.original = QPixmap()
        self.px = QPixmap()
        self.iw = self.ih = 200
        self.degree = 0

        self.shortcuts()
        self.setAcceptDrops(True)
        
        # crop init settings
        self.crop = False
        self.initCrop()
        # future enhancement: crop the primary photo or crop the photo by the ratio
        self.rb = QRubberBand(QRubberBand.Rectangle, self)
        
        self.mm = None
        self.mmd = None
        self.mmon = True
        self.im= None
        self.imd = None
        
        self.file2image('iv.png')

    def shortcuts(self):
        self.cm = QShortcut(QKeySequence("Ctrl+M"), self)
        self.cm.activated.connect(self.showMM)        
        self.ce = QShortcut(QKeySequence("Ctrl+E"), self)
        self.ce.activated.connect(self.showIM)        
        self.oi = QShortcut(QKeySequence("Ctrl+O"), self)
        self.oi.activated.connect(self.open)        
        self.ir = QShortcut(QKeySequence("Ctrl+R"), self)
        self.ir.activated.connect(self.reload)        
        self.iv = QShortcut(QKeySequence("Ctrl+V"), self)
        self.iv.activated.connect(self.paste)        
        self.ic = QShortcut(QKeySequence("Ctrl+C"), self)
        self.ic.activated.connect(self.copy)        
        self.ix = QShortcut(QKeySequence("Ctrl+X"), self)
        self.ix.activated.connect(self.cut)        
        self.iz = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.iz.activated.connect(self.undo)        
        self.ss = QShortcut(QKeySequence("Ctrl+S"), self)
        self.ss.activated.connect(self.save)        
        self.ont = QShortcut(QKeySequence("Ctrl+T"), self)
        self.ont.activated.connect(self.onTop)        
        self.ii = QShortcut(QKeySequence("Ctrl+I"), self)
        self.ii.activated.connect(self.zoomin)        
        self.oo = QShortcut(QKeySequence("Ctrl+U"), self)
        self.oo.activated.connect(self.zoomout)        
        self.oq = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.oq.activated.connect(sys.exit)        
        self.nw = QShortcut(QKeySequence("Ctrl+N"), self)
        self.nw.activated.connect(self.new)        
        self.rb = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.rb.activated.connect(self.mCrop)        
        self.sa = QShortcut(QKeySequence("Ctrl+A"), self)
        self.sa.activated.connect(self.selectAll)        
        self.opp = QShortcut(QKeySequence("+"), self)
        self.opp.activated.connect(self.oplus)        
        self.opm = QShortcut(QKeySequence("-"), self)
        self.opm.activated.connect(self.ominus)        
        
        # functions        
        self.rc = QShortcut(QKeySequence("R"), self)
        self.rc.activated.connect(self.rr)        
        self.rcc = QShortcut(QKeySequence("L"), self)
        self.rcc.activated.connect(self.rl)        
        self._rc = QShortcut(QKeySequence("Alt+R"), self)
        self._rc.activated.connect(self._rr)        
        self._rcc = QShortcut(QKeySequence("Alt+L"), self)
        self._rcc.activated.connect(self._rl)        
        self.mrrH = QShortcut(QKeySequence("H"), self)
        self.mrrH.activated.connect(self.mrh)        
        self.mrrV= QShortcut(QKeySequence("V"), self)
        self.mrrV.activated.connect(self.mrv)        
        self.gray = QShortcut(QKeySequence("G"), self)
        self.gray.activated.connect(self.grayScale)        
        
    def msgBox(self, msg):
        QMessageBox.about(self, "Image Viewer", msg)
        
    def hideMenu(self):
        if self.mm: self.mm.hide()
        if self.im: self.im.hide()
        
    def close2X(self, bmax):
        return self.x() >= bmax

    def close2Y(self, h):
        if self.y() <= 0:
            return 0
        return self.y()
    
    def moveMenu(self, m, d):
        X = self.x()
        Y = self.y()
        if self.close2X(m.bmax):
            X -= m.bmax
        else:
            X += self.width()
        Y = self.close2Y(m.height())
        m.move(X, Y)
        m.show()

    def showMM(self):
        self.hideMenu()
        self.mmon = True
        self.imon = False
        if not self.mmd: 
            self.mm = Menu(self)
            self.mmd = self.mm.d()
        self.moveMenu(self.mm, self.mmd)
        
    def showIM(self):
        self.hideMenu()
        self.mmon = False
        self.imon = True
        if not self.imd: 
            self.im = Menu(self)
            self.imd = self.im.d()
        self.moveMenu(self.im, self.imd)
        
    # functions 
    # qimage grayscale convert by build in function
    def qgc(self, image):
        self.image = image.convertToFormat(QImage.Format_Grayscale8)
        self.px = QPixmap(self.image)
            
    def grayScale(self):
        self.qgc(self.image)
        
    def setOpacity(self, image):
        newImage = QImage(image.size(), QImage.Format_ARGB32)
        newImage.fill(Qt.transparent)
        painter = QPainter(newImage)
        painter.begin(self)
        painter.setOpacity(self.opacity)
        painter.drawImage(QPoint(0, 0), image)
        painter.end()
        return QPixmap.fromImage(newImage)
        
    def oplus(self):
        if self.opacity < 1:
            self.opacity += 0.01
        QToolTip.showText(self.pos(), "Opacity: %02d%%" % (self.opacity*100))
    
    def ominus(self):
        if self.opacity > 0.06:
            self.opacity -= 0.01
        QToolTip.showText(self.pos(), "Opacity: %02d%%" % (self.opacity*100))
    
    def rotate(self, angle):
        self.degree += angle
        px = self.original
        px = px.transformed(
            QTransform().rotate(self.degree), 
            mode = Qt.SmoothTransformation
        )
        rect = QRect( 0, 0, px.width(), px.height() )
        self.px = px.copy(rect)
        QToolTip.showText(QCursor.pos(), "Rotation Degree: %d\xB0" % self.degree)
        self.reDraw(px)
    
    def _rotate(self, angle):
        px = self.imgSize()
        px = px.transformed(
            QTransform().rotate(angle),
            mode = Qt.SmoothTransformation
        )
        QToolTip.showText(QCursor.pos(), "Rotation Degree: %d\xB0" % self.degree)
        self.reDraw(px)
    
    def flip(self, a, b):
        px = self.imgSize()
        px = px.transformed(QTransform().scale(a, b))
        self.reDraw(px)
        
    def reDraw(self, px):
        self.px = px
        self.iw = px.width()
        self.ih = px.height()
        self.resize(px.width(), px.height())
        self.center()
        
    # rotation and flip    
    def rr(self):
        self.rotate(1)
    def rl(self):
        self.rotate(-1)
    def _rr(self):
        self.degree += 90
        self._rotate(90)
    def _rl(self):
        self.degree += -90
        self._rotate(-90)
    def mrh(self):
        self.flip(-1, 1)
    def mrv(self):
        self.flip(1, -1)
        
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, e):
        nn = 0
        for url in e.mimeData().urls():
            f = url.toLocalFile()
            if os.path.isfile(f):
                if nn == 0:
                    self.file2image(f)
                else:
                    run = runit(f)
                    self.threadpool.start(run)
                nn += 1

    # select all crop mode
    def selectAll(self):
        if self.crop: 
            self.mx = 0
            self.my = 0
            self.xw = self.width()
            self.yw = self.height()        
            rect = QRect(0, 0, self.xw, self.yw)
            self.rb.setGeometry(rect.normalized())
            self.rb.show()
        else: 
            self.msgBox("Crop mode needs to be turned on")
            
    # menu changes fo the crop mode
    def mCrop(self):
        if self.crop: 
            if self.mm: self.mm.bcrop.setText("Crop Ctrl+Shift+C")
            if self.im: self.im.bcrop.setText("Crop Ctrl+Shift+C")
            print("crop closed")
            self.closeRB()
        else: 
            if self.mm: self.mm.bcrop.setText("Off Crop  Ctrl+Shift+C")
            if self.im: self.im.bcrop.setText("Off Crop  Ctrl+Shift+C")
            print("crop turned on")
            self.crop = True
            
    # toggle for window on top mode 
    def onTop(self):
        self.hide()
        if self._top:
            if self.mm: self.mm.bot.setText("Off Top Ctrl+T")
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            if self.mm: self.mm.bot.setText("On Top Ctrl+T")
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self._top = not self._top
        self.show()
        
    def file2image(self, f):
        image = QImage(f)
        if image.isNull():
            self.msgBox("Cannot load %s." % f)
            return False
        self.image = image
        self.reload()
        return True
    
    def new(self):
        run = runit("")
        iv.threadpool.start(run)
        
    def open(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open Image", QDir.currentPath())
        if f:
            self.degree = 0
            return self.file2image(f)
        else:
            return False

    def initCrop(self):
        self.cropped = False
        self.mx = 0
        self.my = 0
        self.xw = 0
        self.yw = 0
        
    def closeRB(self, b=True):
        if b:
            self.crop = False
            self.initCrop()
            self.rb.hide()
            return True
        else:
            self.crop = True
            QApplication.restoreOverrideCursor()
            return False
            
    def undo(self):
        
        if self.crop: self.closeRB()
        
        px = self.original
        if not px.isNull():
            self.px = px
            self.iw = px.width()
            self.ih = px.height()
            self.resize(px.width(), px.height())
            
    def reload(self):
        
        if self.crop: self.closeRB()
        
        if self.noImage(): 
            self.open()
        else:
            px = QPixmap(self.image)
            self.px = px
            self.original = px
            self.iw = px.width()
            self.ih = px.height()
            self.resize(px.width(), px.height())
            self.center()

    def paste(self):
        try:
            cb = QApplication.clipboard()
            px = cb.pixmap(mode=cb.Clipboard)
            if not px.isNull():
                self.px = px
                self.image = px.toImage()
                self.reload()                
                self.center()
                return True
            else:
                self.msgBox("No Image found in Clipboard")
                return False
        except IOError as e:
            self.msgBox("Error occurs: " + str(e))
            return False
            
    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())        
        
    def imgSize(self):
        return self.scalePX(self.px, self.iw, self.ih)
    
    def scalePX(self, px, w, h):
        return px.scaled(w, h, Qt.KeepAspectRatio, transformMode = Qt.SmoothTransformation)
        
    def getPX(self):
        px = self.imgSize()
        rect = QRect( self.mx, self.my, self.xw, self.yw )
        return px.copy(rect)
    
    def setCB(self, px):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setPixmap(px, mode=cb.Clipboard)
        
    def cut(self):
            
        if self.crop:
            px = self.getPX()
            self.iw = px.width()
            self.ih = px.height()
            self.closeRB()
        else:
            px = QPixmap(self.image)
            
        self.setCB(px)
        self.px = px
        self.resize(self.iw, self.ih)
        if self.rb.isVisible(): self.center()
            
        if px.isNull():
            self.msgBox("No Image found in Image Viewer")
            return False
        else:
            return True
                     
    def copy(self):
        
        if self.crop:
            px = self.getPX()
            self.closeRB()
        else:
            px = QPixmap(self.image)
                
        self.setCB(px)
        
        if px.isNull():
            self.msgBox("No Image found in Image Viewer")
            return False
        else:
            return True
                     
    def save(self):
        if not self.px.isNull():
            f, _ = QFileDialog.getSaveFileName(
                self,
                c.SF[0],
                "",
                "PNG (*.png);;JPEG (*.jpg *.jpeg)"
            ) 
            if f:
                px = self.imgSize()
                image = px.toImage()
                px = self.setOpacity(image)
                px.save(f)
                return True
            else:
                return False
        else:
            return False
            
    def noImage(self):
        return self.image.isNull()
    
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setOpacity(self.opacity)
        if self.noImage():
            return
        else:
            rect = painter.viewport()
            px = self.imgSize()
            painter.drawPixmap(0, 0, px)
            
        if self._tb1:
            self._tb1.setText(self.digitTime())
        if self._tb2:
            self._tb2.setText(self.digitTime())

    def digitTime(self):
        text = time.strftime("%H" + ":" + "%M" + ":" + "%S")
        return text

    def wheelEvent(self, e):
        step = e.angleDelta()
        s = step.y()
        if s > 0:
            self.zoomin()
        else:
            if self.width() > 30:
                self.zoomout()

    def setFactor(self, fact):
        self.iw = self.iw * fact
        self.ih = self.ih * fact

    def zoomin(self):
        self.setFactor(self.rin)
        self.resize(self.iw, self.ih)

    def zoomout(self):
        self.setFactor(self.rout)
        self.resize(self.iw, self.ih)

    def mouseDoubleClickEvent(self, e):
        self.hideMenu()
        if e.button() == Qt.LeftButton:
            self.open()
            
    def mousePressEvent(self, e):
        self.offset = e.pos()
        self._tip = None
        
        self.hideMenu()
            
        if e.button() == Qt.RightButton:
            self.showMM()
        
        elif e.button() == Qt.MiddleButton:
            if self.crop:
                if self.closeRB(): self.crop = True
            else:    
                self.close()
        
        elif e.button() == Qt.LeftButton:
            if self.crop:
                if self.cropped:
                    QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                else:
                    QApplication.restoreOverrideCursor()
                    self.rb.setGeometry(QRect(self.offset, QSize()))
                    self.rb.show()                
            else:
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, e):
        self._tip = e.pos()
        if self.rb.isVisible(): 
            self.cropped = True
            if not self.xw: 
                self.xw = abs(e.pos().x()-self.offset.x())
            if not self.yw: 
                self.yw = abs(e.pos().y()-self.offset.y())
            if not self.mx:
                self.mx = e.pos().x() - self.xw
            if not self.my:
                self.my = e.pos().y() - self.yw
            print("cropped: [%d,%d,%d,%d]" % (self.mx,self.my,self.xw,self.yw))
            if self.cropOK():
                self.px = self.imgSize()
                QToolTip.showText(
                    self.mapToGlobal(e.pos()), 
                    'Esc to cancel selection, Ctrl+A to select all',
                    self
                )
            else:
                if self.closeRB(): self.crop = True
        QApplication.restoreOverrideCursor()
        
    def cropOK(self):
        return self.rb.width() > 0
    
    def mouseMoveEvent(self, e):
        if self.crop:
            mx = e.pos().x() - int(self.xw/2)
            my = e.pos().y() - int(self.yw/2)
            QToolTip.showText(
                self.mapToGlobal(e.pos()), 
                '(%d, %d)' % (mx, my),
                self
            )
            if self.cropped:
                self.mx = mx
                self.my = my
                self.rb.move(self.mx, self.my)
            else:
                self.rb.setGeometry(QRect(self.offset, e.pos()).normalized())
        else:
            x = e.globalX()
            y = e.globalY()
            xw = self.offset.x()
            yw = self.offset.y()
            self.move(x - xw, y - yw)

    def enterEvent(self, e):
        self._tip = e.pos()
        if self.noImage():
            QToolTip.showText(
                self.mapToGlobal(e.pos()), 
                "Double or right click to open image", 
                self
            )
        if self.crop:
            QApplication.restoreOverrideCursor()
        else:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)

    def leaveEvent(self, e):
        self._tip = None
        QApplication.restoreOverrideCursor()

    def keyPressEvent(self, e):
        key = e.key()
        x = self.x()
        y = self.y()
        off = 5
        
        if key == Qt.Key_Left:
            x -= off
        if key == Qt.Key_Right:
            x += off
        if key == Qt.Key_Up:
            y -= off
        if key == Qt.Key_Down:
            y += off
        self.move(x, y)
        
        s, H, h, W, w = self.loc()
        print("%d, %d" % (W,H))
        if key == 55:
            self.move(0, 0)   
        if key == 57:
            self.move(W-w, 0)   
        if key == 53:
            # self.move((W-w)/2, (H-h)/2)   
            self.center()
        if key == 51:
            self.move(W-w, H-h)   
        if key == 49:
            self.move(0, H-h)   
            
        if key == Qt.Key_Escape:
            if self.crop:
                if self.rb.isVisible():
                    if self.closeRB(): self.crop = True
                else:
                    self.mCrop()
                    QApplication.setOverrideCursor(Qt.PointingHandCursor)
            
    def loc(self):
        # s = QDesktopWidget().screenGeometry()
        s = QApplication.desktop()
        H = s.height()
        h = self.height()
        W = s.width()
        w = self.width()
        return s, H, h, W, w
            

if __name__ == '__main__':

    app = QApplication(sys.argv)
    print(sys.argv)
    nn = 0
    iv = IV()
    try:
        for f in sys.argv[1:]:
            if os.path.isfile(f):
                if nn == 0:
                    iv.file2image(f)
                    iv.show()
                else:
                    run = runit(f)
                    iv.threadpool.start(run)
                nn += 1
    except IOError as e:
        iv.msgBox("invalid file - %s" % str(e))
        
    if nn == 0:
        iv.show()
        
    sys.exit(app.exec_())
