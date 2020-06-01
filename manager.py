import N5700SCPI
import time 
import socket
import struct 

INTERFACE_ADDRESS = 'localhost'
INTERFACE_PORT = 8090
DEST_ADDRESS = 'localhost'
DEST_PORT = 8091

if __name__=="__main__":
    ip = '192.168.1.23'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.1)
    sock.bind((INTERFACE_ADDRESS, INTERFACE_PORT))
    while True:
        try:
            print "Connecting to power supply at %s..."%ip
            ps = N5700SCPI.N5700SCPI(ip)
            if ps.connect():
                Vc = None
                Vm = None
                Ic = None
                Im = None
                out = None
                while True:
                    
                    try:
                        Vm = ps.getActualVoltage()
                        Im = ps.getActualCurrent()
                        out = ps.getOutputState()
                        Vc = ps.getCommandedVoltage()
                        Ic = ps.getCommandedCurrent()
                        print out, Vc, Vm, Ic, Im 
                        datastr = struct.pack('ffff?', Vc, Vm, Ic, Im, out)
                        sock.sendto(datastr, (DEST_ADDRESS, DEST_PORT))
                        try:
                            recdata, recaddr = sock.recvfrom(1024)
                            print "Received \"%s\" from %s"%(recdata, recaddr)
                            if recdata == "outon":
                                ps.setOutputState(True)
                            elif recdata == "outoff":
                                ps.setOutputState(False)
                        except socket.timeout:
                            pass
                    except KeyboardInterrupt:
                        raise
                    except:
                        break
        except KeyboardInterrupt:
            break
        finally:
            ps.close()
            raise