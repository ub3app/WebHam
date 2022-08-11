import glob
import sys
import serial


class SerialUtil:
    def __init__(self):
        pass

    def getAvailablePorts(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial()
                s.port = port
                s.rts = False
                s.dtr = False
                s.open()
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        return result
