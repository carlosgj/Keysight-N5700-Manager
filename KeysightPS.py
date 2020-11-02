import socket
import time
import struct
import re

class KeysightPS():
    def __init__(self, address, port=5025, timeout=5):
        self.address = address
        self.port = port
        self.timeout = timeout
        self.connected = False
        self.sock = None
        self.channelCount = None
        self.channels = []

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        try:
            self.sock.connect((self.address, self.port))
            self.connected = True
            self.getChannels()
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
            
    def getIDInfo(self):
        rawstr = self.query("*IDN?")
        chunks = rawstr.split(',')
        mfr = chunks[0]
        assert mfr == "Keysight Technologies"
        model = chunks[1]
        sn = chunks[2]
        software = chunks[3]
        return {"model":model, "serial_number":sn, "software_version":software}
            
    def getChannels(self):
        #return int(self.getNumber("SYST:CHAN:COUN?")) This returns the number of physical channels, without considering groups
        grpstr = self.query("SYST:GRO:CAT?")
        assert grpstr is not None and len(grpstr) > 2
        REGEX = '''\"([\d,]+)\"''' #Yeah, I know, fuck regexes
        groups = re.findall(REGEX, grpstr)
        #print groups
        for g in groups:
            self.channels.append(int(g[0]))
        self.channelCount = len(self.channels)

    def close(self):
        self.sock.close()
        self.connected = False


if __name__ == "__main__":
    this = KeysightPS("192.168.1.28",timeout=1)
    this.connect()

    try:
        print this.getIDInfo()
    except KeyboardInterrupt:
        pass
    finally:
        this.close()
