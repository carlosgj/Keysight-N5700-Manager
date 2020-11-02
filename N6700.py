import socket
import time
import struct
import re
import KeysightPS

class N6700(KeysightPS.KeysightPS):            
    def getChannels(self):
        #return int(self.getNumber("SYST:CHAN:COUN?")) This returns the number of physical channels, without considering groups
        grpstr = self.query("SYST:GRO:CAT?")
        assert grpstr is not None and len(grpstr) > 2
        REGEX = '''\"([\d,]+)\"''' #Yeah, I know, fuck regexes
        groups = re.findall(REGEX, grpstr)
        print groups
        for g in groups:
            self.channels.append(int(g[0]))
        self.channelCount = len(self.channels)

    def getCommandedVoltage(self, channel):
        return self.getNumber("SOUR:VOLT:LEV? (@%d)"%channel)

    def getActualVoltage(self, channel):
        return self.getNumber("MEAS:VOLT? (@%d)"%channel)

    def getCommandedCurrent(self, channel):
        return self.getNumber("SOUR:CURR:LEV? (@%d)"%channel)

    def getActualCurrent(self, channel):
        return self.getNumber("MEAS:CURR? (@%d)"%channel)

    def getOutputState(self, channel):
        return self.getBool("OUTP:STAT? (@%d)"%channel)
        
    def setOutputState(self, channel, state):
        if state:
            self.query("OUTP:STAT ON", noread=True)
        else:
            self.query("OUTP:STAT OFF", noread=True)
            
    def getQuestionableCond(self, channel):
        idx = self.channels.index(channel)
        return self.getAllQCs()[idx]
        
    def getAllVoltages(self):
        grpstr = ','.join([str(x) for x in self.channels])
        rawstr = self.query("MEAS:VOLT? (@%s)"%grpstr)
        return [float(x) for x in rawstr.split(',')]
        
    def getAllCurrents(self):
        grpstr = ','.join([str(x) for x in self.channels])
        rawstr = self.query("MEAS:CURR? (@%s)"%grpstr)
        return [float(x) for x in rawstr.split(',')]
        
    def getAllOutputStates(self):
        grpstr = ','.join([str(x) for x in self.channels])
        rawstr = self.query("OUTP:STAT? (@%s)"%grpstr)
        return [bool(int(x)) for x in rawstr.split(',')]
        
    def getAllQCs(self):
        grpstr = ','.join([str(x) for x in self.channels])
        rawstr = self.query("STAT:QUES:COND? (@%s)"%grpstr)
        result = []
        #Break down 16-bit ints into bits per N6700 Programmer's Reference Guide
        for num in [int(x) for x in rawstr.split(',')]:
            bits = '{:016b}'.format(num)
            vals = [x=='1' for x in bits]
            defs = ['OVP', 'OCP', 'PFL', 'CP+', 'OTP', 'CP-', 'OV-', 'LM+', 'LM-', 'INH', 'UNR', 'PRO', 'OSC']
            retdict = {}
            for i, d in enumerate(defs):
                retdict[d] = vals[-1-i]
            result.append(retdict)
        #Returns a list of dicts
        return result

    def close(self):
        self.sock.close()
        self.connected = False


if __name__ == "__main__":
    this = N6700SCPI("192.168.1.28",timeout=1)
    this.connect()
    while True:
        try:
            starttime = time.time()
            print this.getAllQCs()
            print time.time() - starttime
        except KeyboardInterrupt:
            break
    this.close()
