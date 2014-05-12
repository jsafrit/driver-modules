#-------------------------------------------------------------------------------
# Name:        TestChamber.py
# Purpose:     General interface to remotely control CSZ Environmental Chambers
#
# Author:      jlsafrit
#
# Created:     23/04/2014
# Copyright:   (c) jlsafrit 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import serial
import struct
#import binascii
from time import sleep, time, ctime
import os
lib_path = os.path.abspath('P:\Development Team\Software\Test Scripts\_Modules')
#lib_path = os.path.abspath('..\_Modules')
sys.path.append(lib_path)

from ModbusCRC import computeCRC, checkCRC


ovenAddr = 1
cmdReg = {'R':3,'W':6}
reg =   {
        'TempSP':60,
        'TempPV':61,
        'TempPCT':62,
        'HumdSP':72,
        'HumdPV':73,
        'HumdPCT':74,
        'EventCtl':22
        }

lowTempLimit = -50
highTempLimit = 85
lowHumdLimit = 0
highHumdLimit = 100

tempThreshold = 2
humdThreshold = 5

class EvtCtl:
    temp = 1
    humd = 2
    purge = 8


class TempChamber:
    """Temperature Chamber object:
    General interface to the chamber controls.

      params:
        comm  -  Comm Port of Chamber (i.e. 'COM16')
    """
    def __init__(self, comm):
        self.comm = comm
        self.baud = 9600
        self.timeout = 1
        self.writeTimeout = 1
        self.isOpen = False
        self.ser = None
        self.result = None
        self.open()

    def open(self):
        try:
            self.ser=serial.Serial( self.comm, self.baud,
                                    timeout=self.timeout,
                                    writeTimeout=self.writeTimeout)
        except serial.serialutil.SerialException:
            print 'BOOM! @ %s' % self.comm
            #raise serial.serialutil.SerialException
        if not self.ser or not self.ser.isOpen():
            print "Problem opening port. Exiting..."
            sys.exit(3)
        else:
            self.isOpen=True

    def close(self):
        self.ser.close()
        if self.ser.isOpen():
            print "Problem closing port. Exiting..."
            sys.exit(3)
        self.isOpen = False

    def readCmd(self, pkt):
        self.ser.write(pkt)
        sleep(.1)
        result=self.ser.read(7)
        if checkCRC(bytearray(result[:-2]),extractCSum(result)):
            self.result=result
            return True
        return False

    def writeCmd(self, pkt):
        self.ser.write(pkt)
        sleep(.1)
        result=self.ser.read(len(pkt))
        if checkCRC(bytearray(result[:-2]),extractCSum(result)) and result==pkt:
            return True
        return False

    def getTemp(self):
        results = [None, None, None]
        if self.readCmd(makePacket('R','TempPV')):
            results[0] = extractData(self.result) / 10.0
        if self.readCmd(makePacket('R','TempSP')):
            results[1] = extractData(self.result) / 10.0
        if self.readCmd(makePacket('R','TempPCT')):
            results[2] = extractData(self.result) / 100.0
        return results

    def getHumd(self):
        results = [None, None, None]
        if self.readCmd(makePacket('R','HumdPV')):
            results[0] = extractData(self.result) / 10.0
        if self.readCmd(makePacket('R','HumdSP')):
            results[1] = extractData(self.result) / 10.0
        if self.readCmd(makePacket('R','HumdPCT')):
            results[2] = extractData(self.result) / 100.0
        return results

    def setTemp(self,temp):
        """Check limits of request and set Temp Setpoint"""
        if not temp:
            return True
        if temp < lowTempLimit:
            print 'Setpoint too low. Minimum value is %d.' % lowTempLimit
            return False
        if temp > highTempLimit:
            print 'Setpoint too high. Maximum value is %d.' % highTempLimit
            return False
        t = int(temp * 10.0)
        #print t
        return self.writeCmd(makePacket('W','TempSP',t))

    def setHumd(self,humd):
        """Check limits of request and set Humidity Setpoint"""
        if not humd:
            return True
        if humd < lowHumdLimit:
            print 'Setpoint too low. Minimum value is %d.' % lowHumdLimit
            return False
        if humd > highHumdLimit:
            print 'Setpoint too high. Maximum value is %d.' % highHumdLimit
            return False
        h = int(humd * 10.0)
        #print h
        return self.writeCmd(makePacket('W','HumdSP',h))

    def setControls(self, Temp=False, Humdity=False, DryAirPurge=False):
        #print 'Setting Controls...',
        e = 0
        if Temp:
            e |= EvtCtl.temp
        if Humdity:
            e |= EvtCtl.humd
        if DryAirPurge:
            e |= EvtCtl.purge
        #print e
        return self.writeCmd(makePacket('W','EventCtl',e))

    def updateStatus(self):
        print 'Current conditions:'
        print ' Temp:   ', self.getTemp()
        print ' Humdity:', self.getHumd()

    def waitSoak(self,waitTime=0,Temp=None,Humdity=None):
        print 'Start Wait at', ctime()
        waitT = bool(Temp)
        waitH = bool(Humdity)

        # Check for you setpoint conditions
        if waitT or waitH:
            print 'Waiting for setpoints.',
            cnt = 0
        while waitT or waitH:
            sleep(30)
            if waitT:
                t = self.getTemp()[0]
                if abs(t - Temp) < tempThreshold:
                    print
                    self.updateStatus()
                    print 'Temperature Setpoint Met.',
                    waitT = False
            if waitH:
                h = self.getHumd()[0]
                if abs(h - Humdity) < humdThreshold:
                    print
                    self.updateStatus()
                    print 'Humdity Setpoint Met.',
                    waitH = False
            print '\b.',
            cnt += 1
            if cnt >= 8:
                cnt = 0
                print
                self.updateStatus()
                print 'Waiting for setpoints.',

            if not waitT and not waitH:
                print

        # Now wait for soak time
        print 'Starting Soak Time at', ctime()
        print 'Estimated completion at', ctime(time()+waitTime)
        endTime = time() + waitTime
        while endTime > time():
            remain_time = "%d sec remaining..." % (endTime-time())
            print remain_time,"           \r",
            sleep(1)
        print

def makePacket(rw='R',rg='TempPV',data=None):
    pkt = bytearray()
    pkt.append(ovenAddr)
    pkt.append(cmdReg[rw])
    pkt.append(0)
    pkt.append(reg[rg])
    if rw=='R':
        pkt.append(0)
        pkt.append(1)
    if rw=='W' and data is not None:
        if data < 0:
            data = 65535 - abs(data) + 1
        pkt.append(data/256)
        pkt.append(data%256)

    csum = computeCRC(pkt)
    pkt.append(csum/256)
    pkt.append(csum%256)

    #print binascii.hexlify(pkt)
    return pkt

def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val

def extractCSum(pkt):
    """extract the checksum from a packet and return as int"""
    return struct.unpack('!H',pkt[-2:])[0]

def extractData(pkt):
    """do 2s compliment on returned data"""
    return twos_comp(int(pkt[3:5].encode('hex'),16), 16)


def main():
    print '\n**** Begin Test'

    print '** Initializing Chamber communications.'
    chamb = TempChamber('COM16')

    chamb.updateStatus()
    print

    print '** Setting Temp & Humdity.'
    temperature=float(input('Enter Temperature in C: '))
    if not chamb.setTemp(temperature):
        print 'Failed to set Temperature!'
    humidity=float(input('Enter Humdity in %: '))
    if not chamb.setHumd(humidity):
        print 'Failed to set Humdity!'

    chamb.updateStatus()
    print

    print '** Turn on Chamber Controls.'
    if not chamb.setControls(True,True,True):
        print 'Failed to set controls!'

    print '** Wait for setpoints and soak.'
    chamb.waitSoak(60, temperature, humidity)

    chamb.waitSoak(30)

    print '\n** Turning off controls.'
    if not chamb.setControls():
        print 'Failed to set controls!'

    print '\n**** Test Complete!'


if __name__ == '__main__':
    main()
