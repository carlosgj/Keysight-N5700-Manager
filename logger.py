import N6700SCPI
import time 
from datetime import datetime
import struct 
from math import ceil, floor
import csv
import os 
from curses import wrapper
import curses

SUPPLIES = [
("Test PS 1", "192.168.1.36", ["pwra", 'pwrb', 'pwrc']),
("Test PS 2", "192.168.1.36", ["pwrd", 'pwre', 'pwrf', 'PWRG']),
]

LOGPATH = "C:\\Users\\carlosj\\Documents\\Keysight-N5700-Manager"

PSHEIGHT = 8
CHANNELWIDTH = 25

conns = []

logfile = None
csvwt = None
def disconenctAll():
    global conns
    for name, ps, chnames in conns:
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
    for name, ps, chnames in conns:
        for ch in ps.channels:
            header.append("%s Ch %d State"%(name, ch))
            header.append("%s Ch %d V"%(name, ch))
            header.append("%s Ch %d I"%(name, ch))
    csvwt.writerow(header)
    
def drawPSHeader(stdscr):
    #Print PS name header
    for i, (name, ps, chnames) in enumerate(conns):
        linelen = 4 * CHANNELWIDTH
        namelen = len(name)
        shebangCount = linelen - (namelen + 2)
        headerstr = "-"*int(ceil(shebangCount/2)) + ' ' + name + ' ' + "-"*(shebangCount - int(ceil(shebangCount/2)))
        stdscr.addstr(i*PSHEIGHT, 0, '#'*(CHANNELWIDTH * 4 +1))
        stdscr.addstr((i*PSHEIGHT)+1, 0, headerstr)
        headerstr = ""
        assert len(chnames) == ps.channelCount
        paddedChNames = chnames + ['[None]']*(4-len(chnames))
        for chname in paddedChNames:
            linelen = CHANNELWIDTH
            shebangCount = linelen - (len(chname) + 2)
            headerstr += '-'*int(ceil(shebangCount/2))
            headerstr += ' ' + chname + ' ' 
            headerstr += '-'*(shebangCount - int(ceil(shebangCount/2)))
        stdscr.addstr((i*PSHEIGHT)+2, 0, headerstr)
        stdscr.addstr(((i+1)*PSHEIGHT)-1, 0, ' '*(CHANNELWIDTH*4))
        for j in range(3, PSHEIGHT-1):
            for k in range(1, 4):
                stdscr.addstr((i*PSHEIGHT)+j, CHANNELWIDTH*k, '|')
        stdscr.addstr(((i+1)*PSHEIGHT)-1, 0, '#'*(CHANNELWIDTH * 4))
        for j in range(PSHEIGHT):
            stdscr.addstr((i*PSHEIGHT)+j, CHANNELWIDTH*4, '#')

def drawBar(scr, y, x, str, n, val):
    if len(str) > n:
        return
    if val < 0:
        val = 0
    leadingSpaces = int((n- len(str))/2)
    paddedStr = ' '*leadingSpaces + str + ' '*((n-len(str))-leadingSpaces)
    greenStr = paddedStr[:val]
    whiteStr = paddedStr[val:]
    scr.addstr(y, x, greenStr, curses.color_pair(2))
    scr.addstr(whiteStr, curses.color_pair(3))

def main(stdscr):
    stdscr.nodelay(True)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    global conns
    screens = []
    print "Connecting to power supplies..."
    for name, ip, chnames in SUPPLIES:
        print "Connecting to %s at %s..."%(name, ip)
        ps = N6700SCPI.N6700SCPI(ip)
        #if ps.connect():
        print "Connection succeeded."
        ps.channelCount = len(chnames)
        ps.channels = [1, 2,3]
        if len(chnames) == 4:
            ps.channels += [4]
        conns.append((name, ps, chnames))
        #else:
        #    print "Connection failed!"
    openLog()
    try:
        while True:
            stdscr.clear()
            drawPSHeader(stdscr)
            
            #Print actual data
            thisrow = [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")]
            
            for i, (name, ps, chnames) in enumerate(conns):
                #Make sure PS is connected
                #if not ps.connected:
                #    print "Error! %s disconnected."%name
                #    ps.connect()
                
                #vs = ps.getAllVoltages()
                vs = [30.0, 30.0, 30.0, 25]
                #cs = ps.getAllCurrents()
                cs = [0.0, -0.1, 1.0, 3.1]
                #outs = ps.getAllOutputStates()
                outs = [False, True, True, True]
                #qcs = ps.getAllQCs()
                qcs = [{'OVP':False, 'OCP':False}, {'OVP':False, 'OCP':True}, {'OVP':False, 'OCP':False}, {'OVP':False, 'OCP':False}]
                for j, ch in enumerate(ps.channels):
                    chcenter = (j*CHANNELWIDTH)+(int(CHANNELWIDTH/2))
                    Vm = vs[j]
                    Im = cs[j]
                    out = outs[j]
                    qc = qcs[j]
                    outsymb = None
                    outsymbC = None
                    #First check for protection
                    if qc['OVP']:
                        outsymb = 'OVP'
                        outsymbC = 1
                    elif qc['OCP']:
                        outsymb = 'OCP'
                        outsymbC = 1
                    #Otherwise, use output state
                    elif out:
                        outsymb = 'ON'
                        outsymbC = 2
                    else:
                        outsymb = 'OFF'
                        outsymbC = 0
                    stdscr.addstr((i*PSHEIGHT)+3, chcenter-1, outsymb, curses.color_pair(outsymbC))
                    stdscr.addstr((i*PSHEIGHT)+4, chcenter-5, "%6.1f V"%Vm)
                    drawBar(stdscr, (i*PSHEIGHT)+5, chcenter-8, "%6.3f A"%Im, 16, int(Im/0.25))
                    thisrow += [outsymb, "%6.3f"%Vm, "%6.3f"%Im] #Add data to CSV row
            #stdscr.refresh()
            stdscr.move(0,0)
            c = stdscr.getch()
            if c == 3:
                raise KeyboardInterrupt
            csvwt.writerow(thisrow) #Write row to CSV
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        disconenctAll()
        logfile.close()
    except:
        disconenctAll()
        logfile.close()
        raise
        
        
wrapper(main)