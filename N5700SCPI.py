import socket
import time


class N5700SCPI():
    def __init__(self, address, port=5025, timeout=5):
        self.address = address
        self.port = port
        self.timeout = timeout
        self.connected = False
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        try:
            self.sock.connect((self.address, self.port))
            self.connected = True
            return True
        except socket.timeout:
            return False

    def query(self, qstr, noread=False):
        if self.connected:
            self.sock.send(qstr+'\n')
            if not noread:
                time.sleep(0.005)
                respstr = self.sock.recv(100)
                return respstr.strip()
            else:
                return
        else:
            return None

    def getNumber(self, qstr):
        respstr = self.query(qstr)
        try:
            return float(respstr)
        except TypeError:
            print "Unable to convert \"%s\" to number"%respstr
            return float('NaN')

    def getBool(self, qstr):
        respstr = self.query(qstr)
        try:
            return bool(int(respstr))
        except TypeError:
            print qstr
            print "Unable to convert \"%s\" to boolean"%respstr
            return False

    def getCommandedVoltage(self):
        return self.getNumber("SOUR:VOLT:LEV?")

    def getActualVoltage(self):
        return self.getNumber("MEAS:VOLT?")

    def getCommandedCurrent(self):
        return self.getNumber("SOUR:CURR:LEV?")

    def getActualCurrent(self):
        return self.getNumber("MEAS:CURR?")

    def getOutputState(self):
        return self.getBool("OUTP:STAT?")
        
    def setOutputState(self, state):
        if state:
            self.query("OUTP:STAT ON", noread=True)
        else:
            self.query("OUTP:STAT OFF", noread=True)

    def close(self):
        self.sock.close()
        self.connected = False


if __name__ == "__main__":
    this = N5700SCPI("192.168.1.17",timeout=1)
    this.connect()
    while True:
        try:
            print(this.getOutputState())
        except KeyboardInterrupt:
            break
    this.close()
