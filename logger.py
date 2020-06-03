import N6700SCPI
import time 
import struct 
from math import ceil, floor
import csv

SUPPLIES = [
("Test PS 1", "192.168.1.36"),
]


conns = []


def disconenctAll():
    for name, ps in conns:
        print "Disconnecting %s."%name
        ps.close()

print "Connecting to power supplies..."
for name, ip in SUPPLIES:
    print "Connecting to %s at %s..."%(name, ip)
    ps = N6700SCPI.N6700SCPI(ip)
    if ps.connect():
        print "Connection succeeded."
        conns.append((name, ps))
    else:
        print "Connection failed!"
           
try:           
    while True:
        starttime = time.time()
        for name, ps in conns:
            linelen = 1 + (ps.channelCount * 16)
            namelen = len(name)
            shebangCount = linelen - (namelen + 2)
            print "#"*int(floor(shebangCount/2)), name, "#"*int(ceil(shebangCount/2)),
        print
        for name, ps in conns:
            for ch in ps.channels:
                print "|     Ch %d     "%ch,
            print '#',  
        print
        for name, ps in conns:
            if not ps.connected:
                print "Error! %s disconnected."
                ps.connect()
            vs = ps.getAllVoltages()
            cs = ps.getAllCurrents()
            outs = ps.getAllOutputStates()
            qcs = ps.getAllQCs()
            for i, ch in enumerate(ps.channels):
                #Vm = ps.getActualVoltage(ch+1)
                #Im = ps.getActualCurrent(ch+1)
                Vm = vs[i]
                Im = cs[i]
                out = outs[i]
                qc = qcs[i]
                outsymb = None
                #First check for protection
                if qc['OVP']:
                    outsymb = 'OVP'
                elif qc['OCP']:
                    outsymb = 'OCP'
                elif out:
                    outsymb = ' ON'
                else:
                    outsymb = 'OFF'
                print "| %s %04.1f %04.1f"%(outsymb, Vm, Im) ,
            print '#',
        print
        print
        print time.time() - starttime
except KeyboardInterrupt:
    pass
except:
    disconenctAll()
    raise
finally:
    disconenctAll()