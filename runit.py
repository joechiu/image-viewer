import os, time, subprocess
from PyQt5.QtCore import QRunnable, pyqtSlot

DEV = True
if os.path.exists('python36.dll'):
    DEV = False

class runit(QRunnable):    
    def __init__(self, f):
        super(runit, self).__init__()
        self.f = f
        
    @pyqtSlot()
    def run(self):
        if DEV:
            cmd = [ "python", "iv.py", self.f ]
        else:
            cmd = [ "iv.exe", self.f ]
            
        subprocess.call(cmd)
        time.sleep(5)

