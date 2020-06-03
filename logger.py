import N6700SCPI
import time 
from datetime import datetime
import struct 
from math import ceil, floor
import csv
import os 

SUPPLIES = [
("Test PS 1", "192.168.1.36"),
]

LOGPATH = "D:\\FRC\\Keysight-N5700-Manager"

conns = []
logfile = None
csvwt = None
def disconenctAll():
    for name, ps in conns:
        print "Disconnecting %s."%name
        ps.close()

def generateLogfileName():
    utc = datetime.utcnow()
    utcstr = utc.strftime("%Y-%m-%d-%H-%M")
    file = os.path.join(LOGPATH, utcstr+".csv")
    return file

def openLog():
    global logfile
    global csvwt
    if logfile is not None:
        logfile.close()
    path = generateLogfileName()
    print "Opening logfile %s..."%path
    logfile = open(path, 'wb')
    csvwt = csv.writer(logfile)
    header = ['Time']
    for name, ps in conns:
        for ch in ps.channels:
            header.append("%s Ch %d State"%(name, ch))
            header.append("%s Ch %d V"%(name, ch))
            header.append("%s Ch %d I"%(name, ch))
    csvwt.writerow(header)

print "Connecting to power supplies..."
for name, ip in SUPPLIES:
    print "Connecting to %s at %s..."%(name, ip)
    ps = N6700SCPI.N6700SCPI(ip)
    if ps.connect():
        print "Connection succeeded."
        conns.append((name, ps))
    else:
        print "Connection failed!"

openLog()

try:           
    while True:
        #Print PS name header
        for name, ps in conns:
            linelen = 1 + (ps.channelCount * 16)
            namelen = len(name)
            shebangCount = linelen - (namelen + 2)
            print "#"*int(floor(shebangCount/2)), name, "#"*int(ceil(shebangCount/2)),
        print
        
        #Print channel header
        for name, ps in conns:
            for ch in ps.channels:
                print "|     Ch %d     "%ch,
            print '#',  
        print
        
        #Print actual data
        thisrow = [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")]
        
        for name, ps in conns:
            #Make sure PS is connected
            if not ps.connected:
                print "Error! %s disconnected."
                ps.connect()
                
            vs = ps.getAllVoltages()
            cs = ps.getAllCurrents()
            outs = ps.getAllOutputStates()
            qcs = ps.getAllQCs()
            for i, ch in enumerate(ps.channels):
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
                #Otherwise, use output state
                elif out:
                    outsymb = ' ON'
                else:
                    outsymb = 'OFF'
                print "| %s %04.1f %04.1f"%(outsymb, Vm, Im) ,
                thisrow += [outsymb, "%6.3f"%Vm, "%6.3f"%Im] #Add data to CSV row
            print '#',
        print
        
        csvwt.writerow(thisrow) #Write row to CSV
        print
        
except KeyboardInterrupt:
    pass
except:
    disconenctAll()
    logfile.close()
    raise
finally:
    disconenctAll()
    logfile.close()