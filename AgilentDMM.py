import time
import os
import sys
import visa

class DMM():
    def __init__(self,addr="USB0::2391::1543::MY53002179::INSTR"):
        self.addr=addr
        self.DMM=None

    def open(self):
        try:
            self.DMM=visa.instrument(self.addr)
        except visa.VisaIOError, status:
            print 'Boom @ %s' % self.addr
            print status
            #raise visa.VisaIOError
            exit(2)

    def write(self,cmd):
        self.DMM.write(cmd)

    def ask(self,cmd):
        return self.DMM.ask(cmd)

    def waitForDone(self,timeout=90):
        #return self.ask("*OPC?")
        self.write('*OPC')
        endtime = time.time() + timeout
        while not int(self.ask('*ESR?')) & 0x01 and endtime > time.time():
            time.sleep(1)
        if endtime < time.time():
            return False
        return True

    def reset(self):
        self.write("*RST")
        self.waitForDone()

    def beep(self):
        self.write("SYST:BEEP")

    def getID(self):
        return self.ask("*IDN?")

    def getOptions(self):
        return self.ask("*OPT?")

    def isError(self):
        result = self.ask("SYST:ERR?")
        resl = result.split(',')
        if resl[1]=='"No error"':
            return False
        print 'Error: %s' % result
        return True

    def dumpAllError(self):
        while self.isError():
            pass

    def dispMessage(self,msg1,msg2=None):
        if msg1:
            self.write('DISP:WIND1:TEXT "%s"' % msg1)
        if msg2:
            self.write('DISP:WIND2:TEXT "%s"' % msg2)

    def dispClear(self):
        self.write('DISP:WIND1:TEXT:CLE')
        self.write('DISP:WIND2:TEXT:CLE')

    def dispOff(self):
        self.write('DISP OFF')

    def dispOn(self):
        self.write('DISP ON')

    def setupHighSpeedDC(self):
        """
        Setup for 1ms sample rate at 100mV range
        """
        # This setup for maximum resolution and 1ms sample rate
        self.write('CONF:VOLT:DC MIN')      #100mV range
        self.write('VOLT:DC:NPLC 0.06')     #max integration and still get 1ms
        self.write('VOLT:DC:ZERO:AUTO ONCE')#only zero at beginning
        self.write('VOLT:DC:NULL:STAT OFF') #disable null offset

        self.dispOff()                      #display off for max speed
        self.write('SAMP:SOUR TIM')         #sample rate on timing
        self.write('SAMP:TIM 0.001')        #set for 1ms
        #print self.ask('SAMP:TIM?')

    def setSampleCount(self, cnt):
        self.write('SAMP:COUN %d' % cnt)
        #print self.ask('SAMP:COUN?')

    def setTrigger(self,type='EXT'):
        """
        Valid types are 'EXT' and 'BUS'
        """
        if type=='BUS':
            self.write('TRIG:SOUR BUS')
        else:
            self.write('TRIG:SOUR EXT')
            self.write('TRIG:SLOP POS')
        self.write('INIT')

    def getAllData(self):
        chunkSize = 100
        data = []

        dataleft = int(self.ask('DATA:POIN?'))
        while dataleft > chunkSize:
            r = self.ask('DATA:REM? %d' % chunkSize)
            data.append(r)
            dataleft = int(self.ask('DATA:POIN?'))
        if dataleft > 0:
            r = self.ask('DATA:REM? %d' % dataleft)
            data.append(r)

        result = ','.join(data)
        return result.split(',')


def DoDMMTest():
    dmm=DMM()
    dmm.open()
    dmm.reset()
    result = dmm.getID()
    if 'MY53002179' not in result:
        print 'Agilent DMM not found.'
        sys.exit(1)
    print result

    dmm.dumpAllError()

    dmm.setupHighSpeedDC()
    dmm.setSampleCount(5000)

    dmm.setTrigger('BUS')
    dmm.write('*TRG')
    print '*Trigger sent...'
    dmm.dispMessage('trigger', 'sent')

    dmm.waitForDone(20)

    rlist = dmm.getAllData()
    print len(rlist)
    for i,v in enumerate(rlist):
        print '%d\t:%0.7f' % (i,float(v))

    dmm.dispOn()
    dmm.dispClear()
    dmm.dispMessage('Capture', 'Complete')
    #print dmm.ask('SYST:ERR?')
    dmm.dumpAllError()


def main(argv):

    print '============================================='
    DoDMMTest()
    print '============================================='
    print 'Testing Complete'

if __name__ == "__main__":
    main(sys.argv[1:])
