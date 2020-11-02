import socket
import time


class N5700SCPI():
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


if __name__ == "__main__":
    this = N5700SCPI("192.168.1.17",timeout=1)
    this.connect()
    while True:
        try:
            print(this.getOutputState())
        except KeyboardInterrupt:
            break
    this.close()
