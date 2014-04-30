import time
import os
import sys
import visa

class PS():
    def __init__(self,addr="USB0::0x0957::0x0807::N5745A-US13E6401L::0::INSTR"):
        self.addr=addr
        self.PS=None

    def open(self):
        try:
            self.PS=visa.instrument(self.addr)
        except visa.VisaIOError, status:
            print 'Boom @ %s' % self.addr
            print status
            #raise visa.VisaIOError
            exit(2)

    def write(self,cmd):
        self.PS.write(cmd)

    def ask(self,cmd):
        return self.PS.ask(cmd)

    def waitForDone(self):
        return self.ask("*OPC?")

    def reset(self):
        self.write("*RST")
        self.waitForDone()

    def getID(self):
        return self.ask("*IDN?")

    def getOptions(self):
        return self.ask("*OPT?")

    def outputOn(self):
        self.write("OUTP ON")
        self.waitForDone()

    def outputOff(self):
        self.write("OUTP OFF")
        self.waitForDone()

    def setV(self,v):
        self.write("VOLT %f" % v)
        self.waitForDone()

    def getV(self):
        res = self.ask("VOLT?")
        return float(res)

    def measV(self):
        res = self.ask("MEAS:VOLT?")
        return float(res)

    def setC(self,c):
        self.write("CURR %f" % c)
        self.waitForDone()

    def getC(self):
        res = self.ask("CURR?")
        return float(res)

    def measC(self):
        res = self.ask("MEAS:CURR?")
        return float(res)

    def setCurrProt(self,state):
        self.write("CURR:PROT:STAT %d" % state)
        self.waitForDone()

    def getCurrProt(self):
        res = self.ask("CURR:PROT:STAT?")
        return res

    def isError(self):
        result = self.ask("SYST:ERR?")
        resl = result.split(',')
        if resl[1]=='"No error"':
            return False
        print 'Error: %s' % result
        return True

    def fpLock(self):
        self.write("SYST:COMM:RLST RWL")
        print self.ask("SYST:COMM:RLST?")

    def fpUnlock(self):
        self.write("SYST:COMM:RLST REM")
        print self.ask("SYST:COMM:RLST?")

    def getDelta(self,v1,v2):
        if v1>v2:
            return v1-v2
        return v2-v1

    def waitForStableV(self,v,timeout=10.0):
        start=time.time()
        dv=self.getDelta(self.measV(),v)
        print "Waiting for stable voltage",
        while dv>0.1:
            dv=self.getDelta(self.measV(),v)
            print ".",
            time.sleep(.5)
            end=time.time()
            if end-start > timeout:
                print '\nError: Timeout - Did not get to stable voltage'
                print 'Exiting...'
                sys.exit(2)
        print ". Done."

    def ProfileRampUp(self, startv, endv, deltav, td=0):
        """
        Defines PS Voltage Ramp based on parameters:
          startv - Start Voltage Level
          endv   - End Voltage Level
          deltav - Change in Voltage Level per step
          td     - (Optional) Time Delay in seconds between steps
        """
        print "Starting ProfileRampUp %0.3f to %0.3f with delta %0.3f (td=%0.2f)" % (startv, endv, deltav, td)
        start = time.time()
        voltage = startv
        self.outputOn()
        self.setV(voltage)
        self.waitForStableV(voltage)
        while voltage < endv:
            #print "Setting voltage to :%f" % voltage
            self.setV(voltage)
            if td:
                time.sleep(td)
            voltage+=deltav
        elapsed = time.time() - start
        print 'ProfileRampUp completed in %0.3f seconds.' % elapsed

    def ProfileRampDown(self, startv, endv, deltav, td=0):
        """
        Defines PS Voltage Ramp based on parameters:
          startv - Start Voltage Level
          endv   - End Voltage Level
          deltav - Change in Voltage Level per step
          td     - (Optional) Time Delay in seconds between steps
        """
        print "Starting ProfileRampDown %0.3f to %0.3f with delta %0.3f (td=%0.2f)" % (startv, endv, deltav, td)
        start = time.time()
        voltage = startv
        self.outputOn()
        self.setV(voltage)
        self.waitForStableV(voltage)
        while voltage > endv:
            #print "Setting voltage to :%f" % voltage
            self.setV(voltage)
            if td:
                time.sleep(td)
            voltage-=deltav
        elapsed = time.time() - start
        print 'ProfileRampDown completed in %0.3f seconds.' % elapsed


def DoPSTest2():
    ps=PS()
    ps.open()
    ps.reset()
    result = ps.getID()
    if 'US13E6401L' not in result:
        print 'Agilent PS not found.'
        sys.exit(1)
    print result

    #ps.setV(10.0)
    #ps.outputOn()
    #time.sleep(3)
    #voltage = ps.measV()
    #print 'Voltage is ',voltage
    #print ps.isError()

    ps.setC(5.0)

    print 'Voltage is', ps.getV()
    print 'Current is', ps.getC()

    print 'Current protection is:',
    print ps.getCurrProt()

    ps.setCurrProt(1)

    print 'Current protection is:',
    print ps.getCurrProt()

    ps.ProfileRampUp(10,12,0.05)

    ps.ProfileRampDown(5,2,0.1,1)

    ps.setV(0)
    ps.outputOff()

def DoPSTest():
    # USB0::0x0957::0x0807::N5745A-US13E6401L::0::INSTR
    #print visa.get_instruments_list()

    PS=visa.instrument("USB0::0x0957::0x0807::N5745A-US13E6401L::0::INSTR")
    PS.write("*RST")
    print "*OPC?", PS.ask("*OPC?")

    print "ID:", PS.ask("*IDN?")
    #print "ERR?", PS.ask("SYST:ERR?")

    #PS.write("*TST?")
    #print PS.read()

#    print PS.ask("SYST:COMM:RLST?")
#    PS.write("SYST:COMM:RLST RWL")
#    print PS.ask("SYST:COMM:RLST?")

    #print PS.ask("VOLT?")

    PS.write("VOLT 5")
    print PS.ask("VOLT?")
    print "ERR?", PS.ask("SYST:ERR?")

    print PS.ask("OUTP?")
    PS.write("OUTP ON")
    print PS.ask("OUTP?")
    print "ERR?", PS.ask("SYST:ERR?")

    time.sleep(3)
    PS.write("VOLT:TRIG MAX")
    print "Init Trig"
    PS.write("INIT")

    print "ERR?", PS.ask("SYST:ERR?")

    #print PS.ask("VOLT?")
    print "Before Trig:", PS.ask("MEAS:VOLT?")
    time.sleep(3)

    #print PS.ask("TRIG:SOUR?")

    ##PS.write("*TRG")
    PS.write("TRIG")
    print "*OPC?", PS.ask("*OPC?")
    print "After Trig:", PS.ask("MEAS:VOLT?")

    #print PS.ask("VOLT?")
    print "ERR?", PS.ask("SYST:ERR?")
    time.sleep(10)

    PS.write("OUTP OFF")

    print PS.ask("SYST:COMM:RLST?")
#    PS.write("SYST:COMM:RLST REM")
#    print PS.ask("SYST:COMM:RLST?")

    sys.exit(0)
    return


def main(argv):

    print '============================================='
    DoPSTest2()
    print '============================================='
    print 'Testing Complete'

if __name__ == "__main__":
    main(sys.argv[1:])
