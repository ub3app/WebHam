import subprocess
import serial
from os.path import exists

class RigctlProxy:
    rigctl = "/usr/bin/rigctl"
    cmd = ""
    model_id = ""
    rig_file = ""

    def __init__(self, modelid, rigfile):
        self.model_id = modelid
        self.rig_file = rigfile
        self.cmd = self.rigctl + " -m " + self.model_id + " -r " + self.rig_file

    def isDevice(self):
        if exists(self.rig_file):
            return True
        else:
            return False

    def get_freq(self):
        c = self.cmd + " f"
        f = 0
        if not self.isDevice():
            return f
        
        #print(c)
        proc = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            #print(line.rstrip())
            try:
                f = int(line.rstrip())
            except ValueError as verr:
                pass
            except Exception as ex:
                pass
            break
        return f

    def set_freq(self, f):
        freq = 0
        if not self.isDevice():
            return freq
        try:
            freq = int(f)
        except ValueError as verr:
            return
        except Exception as ex:
            return
        c = self.cmd + " F " + str(freq)
        proc = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return freq

    def get_mode(self):
        c = self.cmd + " m"
        m = ""
        if not self.isDevice():
            return m
        proc = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            m = line.rstrip().decode("utf-8")
            break
        return m

    def set_mode(self, mode):
        if not self.isDevice():
            return mode
        if not mode:
            return
        if mode not in ['USB', 'LSB', 'CW', 'CWR', 'RTTY', 'AM', 'FM']:
            return
        c = self.cmd + " M " + mode + " 0"
        proc = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        return mode

    def set_ptt(self, ptt):
        if not self.isDevice():
            return
        if ptt not in [0, 1]:
            return
        c = self.cmd + " T "
        if ptt == 1:
            c += "1"
        else:
            c += "0"
        #print(c)
        proc = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    def get_ptt(self):
        c = self.cmd + " t"
        ptt = 0
        if not self.isDevice():
            return ptt
        proc = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            # print(line.rstrip())
            try:
                ptt = int(line.rstrip())
            except ValueError as verr:
                pass
            except Exception as ex:
                pass
            break
        return ptt