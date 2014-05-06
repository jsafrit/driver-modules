#-------------------------------------------------------------------------------
# Name:        QT1.py
# Purpose:     General interface to control QT1-L Units for automated test
#
# Author:      jlsafrit
#
# Created:     06/05/2014
# Copyright:   (c) jlsafrit 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import serial
import time
import sys
import os

from Packet import Packet
from CRC16 import CRC16

#####################################################
# QT1 classes
#####################################################
class Module:
    SH=0
    CM=1

class QT1_UUT:
    """QT1_UUT object:
    General interface for the QT1-L unit and controls.

      params:
        comm  -   Comm Port of the power supply (i.e. 'COM8')
        name  -   Name used for logfiles and unit ID (optional)
        io1   -   DigitalIO object that relays and trigger are based on
        relay -   Relay number on manifold to control blow (optional)
        trig  -   Trigger relay to start a blow test (optional)
    """
    trigger = 0x01
    left_button = 0x02
    right_button = 0x04
    no_button = 0x00
    all_button = trigger | left_button | right_button

    def __init__(self,comm,name=None,io1=None,relay=0,trig=0):
        self.comm = comm
        if name:
            self.name = name
        else:
            self.name = comm

        if relay and io1:
            self.relay = relay
            self.r=DigitalIO.Relay(io1,relay)

        if trig and io1:
            self.trig = trig
            self.t=DigitalIO.Relay(io1,trig)
        else:
            self.trig = None

        self.s = None
        comm2 = 'COM'+str(int(comm[3:])+1)
        try:
            self.s = serial.Serial(comm, 38400, timeout=0, writeTimeout=0)
            self.s2 = serial.Serial(comm2, 38400, timeout=0, writeTimeout=0)
        except serial.serialutil.SerialException, status:
            print 'BOOM! @ %s' % self.comm
            print status
            sys.exit(2)
            #raise serial.serialutil.SerialException

        if not self.s or not self.s.isOpen():
            print 'Could not open comm %s' % comm
            sys.exit(2)

        self.s.setRTS(False)
        self.s2.setRTS(False)

        self.filename = name + '.out'
        try:
            self.fo = open(os.path.join(main_dir,data_dir,self.filename), 'a+')
        except IOError, status:
            print 'BOOM! @ %s' % self.filename
            print status
            sys.exit(3)
        self.logMessage('UUT "%s" created at %s\n' % (self.name, getTimeStamp()))

        self.GoHostCmd =  b'\x01\x00\x02\x00\x1C\xB9\xC9'           #returns sernum
        self.GoSleepCmd = b'\x01\x00\x04\x00\x04\x00\x01\x7A\x01'
        self.GoWakeCmd =  b'\x01\x00\x04\x00\x04\x00\x02\x3A\x00'
        self.GoMenuCmd =  b'\x01\x00\x04\x00\x04\x00\x03\xFB\xC0'
        self.DoTestCmd =  b'\x01\x00\x04\x00\x04\x00\x04\xBA\x02'
        self.GetStatus =  b'\x01\x00\x02\x00\x96\x38\x6E'           #returns test status
        self.GetLCD =     b'\x01\x00\x02\x00\xB3\xF9\xB5'           #returns 3 temps & display
        self.SetButtons = b'\x01\x00\x03\x00\xB2'                   # append buttons & CRC
        self.GetBrAC    = b'\x01\x00\x02\x00\x46\x39\xF2'           # returns 1 byte brac reading

        #RX: 01 00 21 00 B2 | 05 C4 03 DD 03 C0 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 2A 20 20 20 20 20 20 20 87 58  ..!........                 *       .X
        #logging.info('Creating QT1 object "%s" on %s', self.name, self.comm)

    def logMessage(self,msg):
        self.fo.write(msg)
        self.fo.flush()

    def setBob(self):
        #print 'BoB ON'
        self.s.setRTS(True)
        self.s2.setRTS(True)
        time.sleep(.2)

    def clrBob(self):
        time.sleep(.2)
        #print 'BoB OFF'
        self.s.setRTS(False)
        self.s2.setRTS(False)

    def close(self):
        self.logMessage('UUT "%s" finished at %s\n' % (self.name, getTimeStamp()))
        self.fo.close()
        self.s.close()
        self.s2.close()

    def goToHost(self):
        #logging.debug('setting host mode')
        self.setBob()
        self.s2.flushInput()
        self.s2.write(self.GoHostCmd)
        self.s.flushInput()
        self.s.write(self.GoHostCmd)
        time.sleep(1)
        self.clrBob()
        response = self.s.read(13)
        response2 = self.s2.read(13)
        return len(response)==13 and len(response2)==13

    def goToSleep(self):
        self.goToHost()
        self.setBob()
        self.s.write(self.GoSleepCmd)
        self.s2.write(self.GoSleepCmd)
        self.clrBob()
        time.sleep(1)
        return True

    def goToWake(self):
        self.setBob()
        #self.s.write(self.GoWakeCmd)
        self.s2.write(self.GoWakeCmd)
        self.clrBob()
        time.sleep(1)
        return True

    def goToMenu(self):
        self.setBob()
        self.s.write(self.GoMenuCmd)
        #self.s2.write(self.GoMenuCmd)
        self.clrBob()
        time.sleep(1)
        return True

    def grabLCD(self):
        x=1
        while(x):
            x-=1
            #response = self.s.read(999)
            #r = response.encode('hex')
            #if len(r)>0:
            #    pass
                #print ':',r
            #self.s.flushInput()
            #time.sleep(.2)
            self.setBob()
            self.s.flushInput()
            self.s.write(self.GetLCD)
            time.sleep(.1)
            response2 = self.s.read(299)
            p=Packet(response2.encode('hex'))
            if p.valid:
                self.clrBob()
                self.pLCD=p
                return p
                #p.dump()
            #else:
                #print 'Invalid Packet:', response2.encode('hex')
                #print
            time.sleep(.2)
            self.clrBob()
        #self.pLCD = None
        return None


    def grabCond(self, module=Module.SH):
        if module==Module.CM:
            port=self.s2
        else:
            port=self.s
        x=1
        while x:
            x-=1
            port.flushInput()
            time.sleep(.2)
            response = port.read(999)
            r = response.encode('hex')
            #print ':' + r + ':'
            if len(r)>0:
                p=Packet(r)
                if p.valid:
                    self.pCond = p
                    return p
                    p.dump()
                    time.sleep(1)
                else:
                    #print 'Invalid Packet:', r
                    time.sleep(.05)
        #self.pCond = None
        return None

    def getMode(self):
        for x in range(5):
            p=self.grabCond()
            if p:
                return p.Mode
            time.sleep(1)
        return -1

    def getBrac(self):
        brac=-1
        x=3
        r=self.goToHost()
        while(x and not r):
            r=self.goToHost()
            x-=1

        if not r:
            return brac

        self.setBob()
        self.s.flushInput()
        self.s.write(self.GetBrAC)
        time.sleep(.1)
        x=5
        while(x):
            response2 = self.s.read(299)
            #print type(response2)
            p=Packet(response2.encode('hex'))
            if p.valid:
                #p.dump()
                brac=p.BrAC
                break
            else:
                print 'Invalid Packet:', response2.encode('hex')
                print

            self.s.flushInput()
            self.s.write(self.GetBrAC)
            time.sleep(.2)
            x-=1

        self.goToSleep()
        self.clrBob()
        return brac

    def getTestMode(self):
        for x in range(5):
            p=self.grabLCD()
            if p:
                return p.Test_Mode
            time.sleep(1)
        return -1

    def setButton(self,button):
        cmd = bytearray.fromhex(self.SetButtons.encode('hex'))
        cmd.append(button)
        crc = bytearray.fromhex('%x'%CRC16(cmd))
        cmd.append(crc[0])
        cmd.append(crc[1])

        self.setBob()
        self.s.flushInput()
        self.s.write(cmd)
        time.sleep(.1)

        x=10
        while(x):
            response2 = self.s.read(299)
            #print 'Packet:', response2.encode('hex')
            p=bytearray.fromhex(response2.encode('hex'))
            if cmd==p:
                #print 'Good'
                #print
                break
            else:
                pass
                #print 'Invalid Packet:', response2.encode('hex')
                #print '-',
            time.sleep(.2)
            x-=1
        self.clrBob()

    def pullTrigger(self):
        #print '-trig-'
        self.setButton(self.trigger)
        self.setButton(self.no_button)

    def pullAll(self):
        #print '-hold all-'
        self.setButton(self.all_button)
        time.sleep(5)
        self.setButton(self.no_button)

    def waitForMode(self, mode, timeout=30):
        print 'Waiting for mode %d' % mode
        while(timeout):
            current_mode = self.getMode()
            if current_mode == mode:
                return True
            time.sleep(1)
            print current_mode,
            timeout-=1
        print 'Never entered mode %d' % mode
        return False

    def waitForTestMode(self, mode, timeout=30):
        print 'Waiting for test mode %d' % mode
        while(timeout):
            current_mode = self.getTestMode()
            if current_mode == mode:
                return True
            time.sleep(1)
            print current_mode,
            timeout-=1
        print 'Never entered test mode %d' % mode
        return False

    def monitorCond(self, timeout=0, module=Module.SH):
        endTime = time.time() + timeout
        while(1):
            p=self.grabCond(module)
            if p:
                p.dump()
            time.sleep(1)
            if (time.time() > endTime) and timeout > 0:
                break

    def wakeAndTest(self):
        self.goToHost()
        time.sleep(2)
        self.goToWake()
        time.sleep(10)
##        self.setButton(self.trigger)
##        self.setButton(self.no_button)

        # wait to wake up
##        time.sleep(3)
##        self.setButton(self.trigger)
##        self.setButton(self.no_button)

        while(1):
            mode=self.getMode()
            if mode==1:
                # wake it up
                print '-1-'
                self.setButton(self.trigger)
                self.setButton(self.no_button)
                time.sleep(2)
            if mode==3:
                print '-3-'
                # in menu mode
                break
            if mode==4:
                print '-4-'
                # already in pre-test
                break
            time.sleep(5)

        if mode==3:
            time.sleep(1)
            # got to menu mode
            self.setButton(self.trigger)
            self.setButton(self.no_button)

        while(1):
            p=self.grabCond()
            if not p:
                print '.',
            else:
                print p.Mode,
                if p.Mode==4:
                    break
            time.sleep(1)

        # ready for the blow
        time.sleep(10)

        # look for run mode
        while(1):
            p=self.grabCond()
            if not p:
                print '.',
            else:
                print p.Mode,
                if p.Mode==5:
                    break
            time.sleep(1)

        time.sleep(5)

        # go out of run mode
        self.setButton(self.all_button)
        time.sleep(5)
        self.setButton(self.no_button)

    def dumpCal(self):
        fname = getFilename(self.name+'_CAL')
        while not self.goToHost():
            print 'Trying to go to host mode...'
            time.sleep(1)

        print 'Dumping Cal Data...'
        self.setBob()
        self.s.flushInput()
        self.s.write('c')
        time.sleep(.5)
        full_cal=self.s.read(5000)

        # remove \r and blank lines
        r = os.linesep.join([s for s in full_cal.splitlines() if s.strip()])
        r = r.replace('\r','')

        try:
            fo = open(os.path.join(main_dir,data_dir,fname), 'a+')
        except IOError, status:
            print 'BOOM! @ %s' % fname
            print status
            sys.exit(3)
        fo.write(r)
        fo.close()

        self.logMessage('UUT "%s" calibration data is in: %s\n' % (self.name, fname))
        self.clrBob()

    def dumpCurves(self):
        fname = getFilename(self.name)
        while not self.goToHost():
            print 'Trying to go to host mode...'
            time.sleep(1)
        print 'Dumping Curve Data...'
        self.setBob()
        self.s.flushInput()
        self.s.write('f')
        time.sleep(.5)

        # changes added to read entire curve dump
        full_curve = ''
        r=self.s.read(9999)
        while len(r)>0:
            full_curve += r
            time.sleep(.5)
            r=self.s.read(9999)

        # remove \r and blank lines
        r = os.linesep.join([s for s in full_curve.splitlines() if s.strip()])
        r = r.replace('\r','')

        try:
            fo = open(os.path.join(main_dir,data_dir,fname), 'a+')
        except IOError, status:
            print 'BOOM! @ %s' % fname
            print status
            sys.exit(3)
        fo.write(r)
        fo.close()

        #self.logMessage('UUT "%s" calibration data is in: %s\n' % (self.name, fname))
        self.clrBob()

    def doBlow(self, pump, soln, duration=7):
        if self.trig:
            self.trig.on()
            #logging.debug('trigger on')
            time.sleep(1)

        #logging.debug('soln on')
        soln.on()
        time.sleep(.1)
        self.r.on()
        time.sleep(.1)
        soln.off()
        time.sleep(.3)

        #logging.debug('pump on')
        pump.on()
        time.sleep(1)
        #logging.debug('pump off')
        pump.off()

        time.sleep(duration)

        if self.trig:
            #logging.debug('trigger off')
            self.trig.off()
            time.sleep(1.5)

        #logging.debug('soln off')
        self.r.off()


#support routines
def getTimeStamp():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def getFilename(prefix=None):
    filename = getTimeStamp().split()[0] + '_' + getTimeStamp().split()[1]
    filename = filename.replace('-','')
    filename = filename.replace(':','')
    if prefix:
        filename = prefix + '_' + filename + '.txt'
    else:
        filename = 'outlog_' + filename + '.txt'
    return filename


def main():
    pass

if __name__ == '__main__':
    main()
