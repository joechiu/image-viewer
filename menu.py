import os, sys, time, signal, math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from c import *

class Menu(QDialog):
    
    def __init__(self, iv):
        super(Menu, self).__init__(iv)

        self.iv = iv
        self.bmax = 0
        
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        
        self.shortcuts()
    
    def shortcuts(self):

        self.cm = QShortcut(QKeySequence("Ctrl+M"), self)
        self.cm.activated.connect(self.iv.showMM)        
        self.ce = QShortcut(QKeySequence("Ctrl+E"), self)
        self.ce.activated.connect(self.iv.showIM)        
        self.oi = QShortcut(QKeySequence("Ctrl+O"), self)
        self.oi.activated.connect(self.iv.open)        
        self.ir = QShortcut(QKeySequence("Ctrl+R"), self)
        self.ir.activated.connect(self.iv.reload)        
        self.av = QShortcut(QKeySequence("Ctrl+V"), self)
        self.av.activated.connect(self.iv.paste)        
        self.ic = QShortcut(QKeySequence("Ctrl+C"), self)
        self.ic.activated.connect(self.iv.copy)        
        self.ix = QShortcut(QKeySequence("Ctrl+X"), self)
        self.ix.activated.connect(self.iv.cut)        
        self.iz = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.iz.activated.connect(self.iv.undo)        
        self.ss = QShortcut(QKeySequence("Ctrl+S"), self)
        self.ss.activated.connect(self.iv.save)        
        self.ot = QShortcut(QKeySequence("Ctrl+T"), self)
        self.ot.activated.connect(self.iv.onTop)        
        self.ii = QShortcut(QKeySequence("Ctrl+I"), self)
        self.ii.activated.connect(self.iv.zoomin)        
        self.oo = QShortcut(QKeySequence("Ctrl+U"), self)
        self.oo.activated.connect(self.iv.zoomout)        
        self.oq = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.oq.activated.connect(sys.exit)        
        self.nw = QShortcut(QKeySequence("Ctrl+N"), self)
        self.nw.activated.connect(self.iv.new)        
        self.rb = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.rb.activated.connect(self.iv.mCrop)        
        self.sa = QShortcut(QKeySequence("Ctrl+A"), self)
        self.sa.activated.connect(self.iv.selectAll)        
        self.opp = QShortcut(QKeySequence("+"), self)
        self.opp.activated.connect(self.iv.oplus)        
        self.opm = QShortcut(QKeySequence("-"), self)
        self.opm.activated.connect(self.iv.ominus)        
        
        # functions        
        self.rc = QShortcut(QKeySequence("R"), self)
        self.rc.activated.connect(self.iv.rr)        
        self.rcc = QShortcut(QKeySequence("L"), self)
        self.rcc.activated.connect(self.iv.rl)        
        self.mrrH = QShortcut(QKeySequence("H"), self)
        self.mrrH.activated.connect(self.iv.mrh)        
        self.mrrV= QShortcut(QKeySequence("V"), self)
        self.mrrV.activated.connect(self.iv.mrv)        
        
    def d(self):
    
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        if self.iv.crop: c.CR = 'Off Crop'
        else: c.CR = 'Crop'
        
        if self.iv._top: c.OT = 'On Top'
        else: c.OT = 'Off Top'
   
        if self.iv.mmon:
            menu = 'Main Menu'
            names = {
                c.IM[0]:c.IM[1], 
                c.OI[0]:c.OI[1], 
                c.ZI[0]:c.ZI[1], 
                c.ZO[0]:c.ZO[1], 
                c.OT:'Ctrl+T',
                c.CT[0]:c.CT[1], 
                c.CP[0]:c.CP[1], 
                c.PT[0]:c.PT[1], 
                c.SF[0]:c.SF[1], 
                c.CR:'Ctrl+Shift+C', 
                c.UD[0]:c.UD[1], 
                c.RL[0]:c.RL[1], 
                c.CL[0]:c.CL[1], 
                c.EX[0]:c.EX[1], 
                "oplus":"+",
                "ominus":"-",
                self.iv._time1:'',
            }
        else:
            menu = 'Image Menu'
            names = {
                c.MM[0]:c.MM[1], 
                c.ZI[0]:c.ZI[1], 
                c.ZO[0]:c.ZO[1], 
                c.RC[0]:c.RC[1], 
                c.RA[0]:c.RA[1], 
                c.MH[0]:c.MH[1], 
                c.MV[0]:c.MV[1], 
                c.CT[0]:c.CT[1], 
                c.CP[0]:c.CP[1], 
                c.PT[0]:c.PT[1], 
                c.CR:'Ctrl+Shift+C', 
                c.UD[0]:c.UD[1], 
                c.RL[0]:c.RL[1], 
                c.CL[0]:c.CL[1], 
                self.iv._time2:'',
            }
        
        row = c.row
        vw  = c.bw    
        vh  = c.bh
        lvl = c.lvl
        for name in names.keys():
            if name == 'Reload' and self.iv.noImage():
                continue
            
            if name == 'oplus' or name == 'ominus':
                b = QPushButton(names[name], self)
                b.setAutoRepeat(True)
                if name == 'oplus':
                    b.resize(vw/2-1, vh - 1)
                    b.move(0, row)
                else:
                    b.resize(vw/2, vh - 1)
                    b.move(vw/2, row)
                    row += vh
            else:
                b = QPushButton(name+" "+names[name], self)
                b.setAutoRepeat(False)
                b.move(0, row)
                b.resize(vw, vh - 1)
                if name == c.OT: setattr(self, "bot", b)
                if name == c.CR: setattr(self, "bcrop", b)
                row += vh
                
            b.clicked.connect(self.do(name, self))
            ss = 'QPushButton { background-color: rgba(0, 0, 0, %d%%); color: #FFF; font-size: 12px; }'
            ss += 'QPushButton:hover:!pressed { background-color: rgba(0, 0, 0, 60%%);border: 1px solid yellow; }'
            b.setStyleSheet(ss % lvl)
            lvl += math.ceil((100 - lvl) / len(names))
            
            if name == self.iv._time1:
                self.iv._tb1 = b
            if name == self.iv._time2:
                self.iv._tb2 = b
            if b.width() > self.bmax:
                self.bmax = b.width()
                
        self.setWindowTitle(menu)
        
        return True
        
    def do(self, v, d):
        def act():
            if v == c.MM[0]:
                self.iv.showMM()
            if v == c.IM[0]:
                self.iv.showIM()
            if v == c.OT:
                self.iv.onTop()
                self.close()
            if v == c.OI[0]:
                if self.iv.open(): self.close()
            if v == c.CT[0]:
                if self.iv.cut(): self.close()
            if v == c.CP[0]:
                if self.iv.copy(): self.close()
            if v == c.PT[0]:
                if self.iv.paste(): self.close()
            if v == c.SF[0]:
                if self.iv.save(): self.close()
            if v == c.ZI[0]:
                self.iv.zoomin()
            if v == c.ZO[0]:
                self.iv.zoomout()
            if v == c.UD[0]:
                self.iv.undo()
                self.close()
            if v == c.CR:
                self.iv.mCrop()
                self.close()
            if v == c.EX[0]:
                sys.exit()
            if v == c.RL[0]:
                self.iv.reload()
                self.close()
            if v == c.CL[0]:
                self.close()
            # image functions                
            if v == c.RC[0]:
                self.iv.rr()
            if v == c.RA[0]:
                self.iv.rl()
            if v == c.MH[0]:
                self.iv.mrh()
            if v == c.MV[0]:
                self.iv.mrv()
            if v == 'oplus':
                self.iv.oplus()
            if v == 'ominus':
                self.iv.ominus()

        return act
    
    def mousePressEvent(self, e):
        if e.button() == Qt.MiddleButton:
            self.close()
