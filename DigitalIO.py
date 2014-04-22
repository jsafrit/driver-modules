''' DigitalIO interface module
This is for controlling digital IO of the DLP-232PC but is expandable for
many serial to IO functional adapter boards
'''
import time
import sys
import serial

OFF= 0
ON = 1
DIN = 2

NUM_CHANNELS=14

#          0     1
LED=    [ '{' , '}' ]

DIO=dict()
# These are inverted here because
# relay card is active low
#          OFF   ON  DIN
DIO[1]= [ '1' , 'Q', 'A' ]
DIO[2]= [ '2' , 'W', 'S' ]
DIO[3]= [ '3' , 'E', 'D' ]
DIO[4]= [ '4' , 'R', 'F' ]
DIO[5]= [ '5' , 'T', 'G' ]
DIO[6]= [ '6' , 'Y', 'H' ]
DIO[7]= [ '7' , 'U', 'J' ]
DIO[8]= [ '8' , 'I', 'K' ]
DIO[9]= [ '/' , 'a', 'b' ]
DIO[10]=[ 'd' , 'e', 'f' ]
DIO[11]=[ 'h' , 'i', 'j' ]
DIO[12]=[ 'l' , 'm', 'n' ]
DIO[13]=[ 'p' , 'q', 'r' ]
DIO[14]=[ 't' , '&', '*' ]

class DigitalIO:
    def __init__(self, comm):
        self.comm = comm
        self.baud = 460800
        self.timeout = 1
        self.ser = None
        self.isOpen = False
        self.minchannel = 1
        self.maxchannel = NUM_CHANNELS
        self.rang=range(self.minchannel,self.maxchannel+1)

    def __str__(self):
        str = 'Comm Port is %s. ' % self.comm
        str += 'Device is '
        if self.isOpen:
            str += 'open.\n'
        else:
            str += 'closed.\n'
        str += 'Min Channel is %d. Max Channel is %d.' % (self.minchannel, self.maxchannel)
        return str

    def ping(self):
        """Pings controller to see if still responding
        returns bool"""
        if not self.isOpen:
            return False
        self.ser.write("'") # ping command
        result = self.ser.read(1)
        if result != 'Q':
            return False
        return True

    def sendCmdIO(self,cmd):
        self.ser.write(cmd)
        return

    def open(self):
        try:
            self.ser=serial.Serial(self.comm, self.baud, timeout=self.timeout)
        except serial.serialutil.SerialException:
            print 'BOOM! @ %s' % self.comm
            #raise serial.serialutil.SerialException

        if not self.ser or not self.ser.isOpen():
            print "Problem opening port. Exiting..."
            sys.exit(3)
        else:
            self.isOpen=True
            if not self.ping():
                print "Problem with IO device not responding. Exiting..."
                sys.exit(3)

    def close(self):
        if not self.isOpen:
            return
        self.ser.close()
        if self.ser.isOpen():
            print "Problem closing port. Exiting..."
            sys.exit(3)
        self.isOpen=False

    def setMinChannel(self,n):
        if n>0 and n<=NUM_CHANNELS:
            self.minchannel=n
            self.rang=range(self.minchannel,self.maxchannel+1)

    def setMaxChannel(self,n):
        if n>0 and n<=NUM_CHANNELS:
            self.maxchannel=n
            self.rang=range(self.minchannel,self.maxchannel+1)

    def setLED(self,state):
        self.sendCmdIO(LED[state])
        return

    def setRelay(self,ch,state):
        if ch not in range(self.minchannel,self.maxchannel+1):
            print 'Invalid Channel. Doing nothing...'
            return False
        if state not in [0,1]:
            print 'Invalid State. Doing nothing...'
            return False
        self.sendCmdIO(DIO[ch][state])
        result=self.ping()
        return result

    def getRelay(self,ch):
        if ch not in range(self.minchannel,self.maxchannel+1):
            print 'Invalid Channel. Doing nothing...'
            return False
        result = None
        self.sendCmdIO(DIO[ch][DIN])
        result=self.ser.read(3)
        #print '::%s::' % result
        return result.strip()

    def setAll(self,state):
        """Set all relay states
        """
        if state not in [0,1]:
            print 'Invalid State. Doing nothing...'
            return False
        for ch in range(self.minchannel,self.maxchannel+1):
            self.sendCmdIO(DIO[ch][state])
        result=self.ping()
        return result

    def setSafe(self):
        return self.setAll(OFF)

    def setAllOff(self):
        return self.setAll(OFF)

    def setAllOn(self):
        return self.setAll(ON)

class Relay:
    def __init__(self,IO,channel):
        self.io=IO
        self.ch=channel
        self.state=OFF

    def set(self,state):
        self.io.setRelay(self.ch,state)
        self.state=state

    def on(self):
        self.set(ON)

    def off(self):
        self.set(OFF)

class DigIn:
    def __init__(self,IO,channel):
        self.io=IO
        self.ch=channel
        self.state=DIN

    def get(self):
        result = self.io.getRelay(self.ch)
        if str(result)[0] == '1':
            return False
        else:
            return True

def DoIOTest():
    io1=DigitalIO('COM10')
    io1.setMaxChannel(8)

    io2=DigitalIO('COM11')
    io2.setMaxChannel(4)

    io1.open()
    io1.setSafe()

    io2.open()
    io2.setSafe()

    print io1
    print io2
    #io1.setAll(ON)
    #time.sleep(3)

    #io1.setAllOff()
    #time.sleep(1)

    for i in io1.rang:
        print "Turning Relay %d" % i
        io1.setLED(OFF)
        io1.setRelay(i,OFF)
        time.sleep(.1)
        io1.setLED(ON)
        io1.setRelay(i,ON)
        time.sleep(.2)
        io1.setLED(OFF)
        io1.setRelay(i,OFF)
        time.sleep(.1)

    io1.setAllOff()

    io2.close()
    io1.close()

    #sys.exit(0)
    return

def DoRelayTest():
    #Open the respective comm ports
    io1=DigitalIO('COM10')
    io1.open()
    io1.setMaxChannel(8)
##    io2=DigitalIO('COM11')
##    io2.open()
##    io2.setMaxChannel(8)

    relay=[]
    # Add relays in block 1
    for i in range(1,8):
        r=Relay(io1,i)
        relay.append(r)
##    # Add relays in block 1
##    for i in range(1,8):
##        r=Relay(io2,i)
##        relay.append(r)

##    #Add ignition control relays
##    ignition=[Relay(io1,8), Relay(io2,8)]
##    print len(relay)
##    relay[0].on()
##    relay[10].on()
##    ignition[0].on()

    for r in relay:
        print r.ch, ':',
        print r.state
        print '---'
        r.on()

##    print 'Ignition 1 is', ignition[0].state
##    print 'Ignition 2 is', ignition[1].state

    #io1.setAllOn()
    time.sleep(5)
    io1.setSafe()
#    io2.setSafe()
    io1.close()
#    io2.close()

    return

def main(argv):
    print '====================================='
    print '= Testing Digital IO Card.'
    print '====================================='
    #DoIOTest()
    #DoRelayTest()
    print '====================================='
    print '= Testing Complete'
    print '====================================='

if __name__ == "__main__":
    main(sys.argv[1:])
